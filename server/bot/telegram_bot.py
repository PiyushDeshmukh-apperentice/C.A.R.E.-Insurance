import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, constants
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

import tempfile
import os
import json

from state_manager import get_session, State
from api_client import (
    login,
    submit_health_claim,
    submit_automobile_claim,
    get_claim_history,
    get_policies,
    get_claim_details
)
from documents import HEALTH_DOCUMENTS
from config import TELEGRAM_TOKEN

# =========================
# CONFIGURATION & CONSTANTS
# =========================

if not hasattr(State, "ASK_HEALTH_ACCIDENT"):
    setattr(State, "ASK_HEALTH_ACCIDENT", "ASK_HEALTH_ACCIDENT")

AUTO_FIELD_PROMPTS = {
    "event_date": "📅 Enter event date (YYYY-MM-DD):",
    "event_time": "⏰ Enter event time (HH:MM):",
    "activity": "💥 Enter activity type (e.g., Road Accident, Theft):",
    "street": "📍 Enter street name:",
    "city": "🏙️ Enter city:",
    "state": "🗺️ Enter state:",
    "driver_name": "👤 Enter driver's name:",
    "driver_age": "🎂 Enter driver's age:",
    "driver_gender": "⚧ Enter driver's gender (Male/Female/Other):",
    "licensed": "🪪 Is the driver licensed? (Yes/No):",
    "experience_years": "⏳ Driving experience (in years):",
    "under_influence": "🍺 Was the driver under influence? (Yes/No):",
    "policy_name": "📜 Enter Policy Name:"
}

AUTO_FIELDS_ORDER = [
    "event_date", "event_time", "activity",
    "street", "city", "state",
    "driver_name", "driver_age", "driver_gender",
    "licensed", "experience_years", "under_influence",
    "policy_name"
]

HEALTH_FILE_EMOJIS = {
    "admission_note": "🏥",
    "prescription": "💊",
    "imaging_report": "🩻",
    "pathology_report": "🔬",
    "discharge_summary": "📄",
    "bill": "🧾",
    "insurance": "🛡️",
    "fir_receipt": "👮"
}

# =========================
# HELPERS
# =========================

def escape_md(text):
    if text is None:
        return "N/A"
    return str(text).replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[")

def progress_bar(i, total):
    return "▓" * i + "░" * (total - i)

async def animate_processing(context, chat_id, message_id):
    steps = [
        ("🔄 *Connecting to Secure Engine...*", 1.0),
        ("🔍 *Analyzing Documents (OCR & AI)...*", 4.0),
        ("📖 *Cross-referencing Policy Clauses...*", 2.0),
        ("🤖 *Finalizing Adjudication...*", 1.5)
    ]
    for text, duration in steps:
        try:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode="Markdown")
            await asyncio.sleep(duration) 
        except Exception:
            pass

def format_submission_report(result, claim_type="health"):
    """
    Robust formatter with Tabular Cost Breakdown.
    """
    
    # 1. Diagnosis Logic
    diagnosis_raw = result.get('diagnosis')
    diagnosis_str = "N/A"
    if isinstance(diagnosis_raw, dict) and diagnosis_raw.get('icd_code'):
        diagnosis_str = f"{diagnosis_raw.get('icd_code')} - {diagnosis_raw.get('description', '')}"
    elif isinstance(diagnosis_raw, str) and len(diagnosis_raw) > 3:
        diagnosis_str = diagnosis_raw

    # 2. Reasons Logic
    reasons = result.get('decision_reasons', [])
    reasons_str = "None"
    if reasons:
        if isinstance(reasons[0], str):
             reasons_str = "\n".join([f"• {r}" for r in reasons])
        elif isinstance(reasons[0], dict):
             reasons_str = "\n".join([f"• {r.get('description', str(r))}" for r in reasons])

    # 3. Clauses Logic
    clauses = result.get('applied_clauses', [])
    clauses_str = "None"
    if clauses:
        clauses_list = []
        for c in clauses:
            if isinstance(c, dict):
                text = c.get('text', c.get('clause_text', 'Clause'))
                page = c.get('policy_page', '?')
                clauses_list.append(f"• {text} (Pg {page})")
            else:
                clauses_list.append(f"• {str(c)}")
        clauses_str = "\n".join(clauses_list)
    
    # 4. Cost Logic (Tabular / Receipt Style)
    cost_str = ""
    if claim_type == "auto":
        breakdown = result.get('cost_breakdown', [])
        if breakdown:
            # Start Code Block for Monospace font
            lines = ["```text"] 
            # Header
            lines.append(f"{'PART':<18} {'COST':>10}")
            lines.append("-" * 30)
            
            for item in breakdown:
                # Handle API key variations ('part_name' vs 'part')
                part_name = item.get('part_name', item.get('part', 'Unknown'))[:18]
                cost_val = item.get('estimated_cost', item.get('cost', 0))
                # Add row
                lines.append(f"{part_name:<18} ₹{cost_val:>9}")
            
            lines.append("-" * 30)
            total = result.get('estimated_cost', 0)
            lines.append(f"{'TOTAL':<18} ₹{total:>9}")
            lines.append("```") # End Code Block
            
            cost_str = "\n📋 *COST BREAKDOWN*\n" + "\n".join(lines)

    # 5. Build Message
    msg = (
        f"✅ *{claim_type.title()} Claim Submitted*\n━━━━━━━━━━━━━━━━━━\n"
        f"🆔 *ID:* `{escape_md(result.get('claim_id', 'PENDING'))}`\n"
        f"📌 *Decision:* {escape_md(result.get('decision', 'N/A'))}\n"
        f"📊 *Confidence:* {result.get('confidence', 0)}%\n\n"
    )
    
    if claim_type == "health" and diagnosis_str != "N/A":
        msg += f"🔍 *Diagnosis:* {escape_md(diagnosis_str)}\n"
    elif claim_type == "auto":
        # Note: We add cost_str directly without escaping because it contains code blocks
        msg += f"💰 *Est. Cost:* ₹{result.get('estimated_cost', 0)}\n{cost_str}\n"

    msg += (
        f"\n📝 *Summary:*\n_{escape_md(result.get('summary', ''))}_\n\n"
        f"📋 *Key Reasons:*\n{escape_md(reasons_str)}\n\n"
        f"📜 *Applied Clauses:*\n{escape_md(clauses_str)}\n\n"
        f"🧾 *Audit Ref:* `{escape_md(result.get('audit_reference_id', 'N/A'))}`"
    )
    return msg

# =========================
# UI MENUS
# =========================

def main_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏥 Health Claim", callback_data="health"), InlineKeyboardButton("🚗 Automobile Claim", callback_data="auto")]])

def claim_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Apply for Claim", callback_data="apply")],
        [InlineKeyboardButton("📋 Claim History", callback_data="history")],
        [InlineKeyboardButton("📄 Active Policies", callback_data="policies")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_main")]
    ])

def post_action_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 View Claim History", callback_data="history")],
        [InlineKeyboardButton("📝 Apply Another Claim", callback_data="apply")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_main")]
    ])

# =========================
# COMMANDS
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session(update.effective_user.id)
    session.clear()
    session["state"] = State.ASK_EMAIL
    banner_url = "AgACAgUAAxkBAAIC3mloGBB-B9_ykav0_zewdqRJgn3iAALJD2sbRDxAV5rDKDof2GJhAQADAgADdwADOAQ"
    welcome_text = "✨ *Welcome to ClaimAuto Bot* ✨\n\nI am your AI assistant for seamless insurance claims.\n👇 *To get started, please enter your registered email:*"
    try:
        await update.message.reply_photo(photo=banner_url, caption=welcome_text, parse_mode="Markdown")
    except:
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_session(update.effective_user.id).clear()
    await update.message.reply_text("❌ Cancelled. Type /start to begin again.")

# =========================
# TEXT HANDLER
# =========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session(update.effective_user.id)
    text = update.message.text.strip()

    if session["state"] == State.ASK_EMAIL:
        session["email"] = text
        session["state"] = State.ASK_PASSWORD
        await update.message.reply_text("🔐 Enter password:")
        return

    if session["state"] == State.ASK_PASSWORD:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING)
        token = login(session["email"], text)
        if not token:
            session["state"] = State.ASK_EMAIL
            await update.message.reply_text("❌ Invalid login. Enter email again:")
            return
        session["token"] = token
        session["state"] = State.MAIN_MENU
        await update.message.reply_text("✅ *Logged in successfully.*\nWhat would you like to do?", parse_mode="Markdown", reply_markup=main_menu())
        return

    if session["state"] == State.ASK_POLICY_NAME:
        processing_msg = await update.message.reply_text("⏳ *Starting analysis...*", parse_mode="Markdown")
        
        is_accident = session.get("is_accident", False)
        # Note: If skip_fir was clicked, 'fir_receipt' will not be in docs
        has_fir = "fir_receipt" in session.get("docs", {})

        if is_accident and has_fir:
            # === ESCALATION ROUTE ===
            await animate_processing(context, update.effective_chat.id, processing_msg.message_id)
            await asyncio.sleep(10)

            escalation_msg = (
                "⚠️ *Claim Escalated*\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "🆔 *ID:* `PENDING_MANUAL_REVIEW`\n"
                "📌 *Status:* Escalated for Manual Verification\n\n"
                "📝 *Reason:* Accident reported with FIR attached. Requires human officer verification.\n"
                "⏳ *Est. Time:* 24-48 Hours"
            )
            
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_msg.message_id)
            await update.message.reply_text(escalation_msg, parse_mode="Markdown", reply_markup=post_action_menu())
        
        else:
            # === STANDARD ROUTE ===
            await animate_processing(context, update.effective_chat.id, processing_msg.message_id)
            try:
                result = submit_health_claim(session["email"], session["token"], text, session["docs"])
                formatted_msg = format_submission_report(result, claim_type="health")
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_msg.message_id)
                await update.message.reply_text(formatted_msg, parse_mode="Markdown", reply_markup=post_action_menu())
            except Exception as e:
                await update.message.reply_text(f"❌ Submission failed: {str(e)}")
        
        session["state"] = State.MAIN_MENU
        return

    if session["state"] == State.ASK_AUTO_DETAILS:
        idx = session.setdefault("auto_step", 0)
        current_field = AUTO_FIELDS_ORDER[idx]
        value_to_save = text

        if current_field in ["licensed", "under_influence"]:
            if text.lower() in ["yes", "y"]: value_to_save = True
            elif text.lower() in ["no", "n"]: value_to_save = False
            else:
                await update.message.reply_text("⚠️ Please answer with 'Yes' or 'No'.")
                return
        
        if current_field == "driver_gender":
            val = text.lower()
            if val not in ["male", "female", "other"]:
                await update.message.reply_text("⚠️ Please enter Male, Female, or Other.")
                return
            value_to_save = val

        if current_field == "activity":
            value_to_save = text.lower().replace(" ", "_")

        session["auto_details"][current_field] = value_to_save
        session["auto_step"] += 1

        if session["auto_step"] < len(AUTO_FIELDS_ORDER):
            next_field = AUTO_FIELDS_ORDER[session["auto_step"]]
            prompt = AUTO_FIELD_PROMPTS.get(next_field, f"Enter {next_field}:")
            progress = progress_bar(session["auto_step"], len(AUTO_FIELDS_ORDER))
            
            # --- RESTORED: Step Counter 1/13 ---
            step_count = f"Step {session['auto_step'] + 1}/{len(AUTO_FIELDS_ORDER)}"
            
            await update.message.reply_text(f"*{step_count}*: {prompt}\n{progress}", parse_mode="Markdown")
        else:
            session["state"] = State.UPLOADING_AUTO_DOCS
            session["doc_index"] = 0
            await update.message.reply_text("📸 *Upload Vehicle Photo:*\n\nYou can send it as a photo or file.", parse_mode="Markdown")
        return

# =========================
# CALLBACK HANDLER
# =========================

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    session = get_session(update.effective_user.id)
    data = query.data

    # --- FIX: SKIP FIR HANDLER ---
    if data == "skip_fir":
        session["doc_index"] += 1
        # Pass 'query' (not update) so we can edit the message
        await trigger_next_health_upload(query, session)
        return

    if data == "accident_yes":
        session["is_accident"] = True
        session["health_docs_list"] = list(HEALTH_DOCUMENTS) + [("fir_receipt", "👮 Upload FIR Receipt (Optional)")]
        session["state"] = State.UPLOADING_HEALTH_DOCS
        session["doc_index"] = 0
        await trigger_next_health_upload(query, session)
        return

    if data == "accident_no":
        session["is_accident"] = False
        session["health_docs_list"] = list(HEALTH_DOCUMENTS)
        session["state"] = State.UPLOADING_HEALTH_DOCS
        session["doc_index"] = 0
        await trigger_next_health_upload(query, session)
        return

    # --- EXISTING HANDLERS ---
    if data.startswith("claim_"):
        parts = data.split("_")
        claim_type = parts[1]
        claim_id = "_".join(parts[2:])
        try:
            claim = get_claim_details(session["token"], claim_id, claim_type)
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")
            return

        decision_data = claim.get('decision', {}) if isinstance(claim.get('decision'), dict) else {}
        decision_val = decision_data.get('decision', claim.get('decision', 'N/A'))
        confidence_val = decision_data.get('confidence', 'N/A')
        summary_val = decision_data.get('reason', 'No summary available')
        clauses_text = "\n".join([f"• {c.get('clause_text', 'N/A')} (Pg {c.get('policy_page', 'N/A')})" for c in claim.get('applied_clauses', [])]) or "None"

        details = ""
        output_image = claim.get('output_image_path') if claim_type == "auto" else None

        if claim_type == "health":
            diagnosis = decision_data.get('diagnosis', {})
            icd_str = ""
            if isinstance(diagnosis, dict) and diagnosis.get('icd_code') not in [None, "N/A"]:
                icd_str = f"\n🏥 *Diagnosis:*\nICD: `{escape_md(diagnosis['icd_code'])}`\n"

            details = (
                f"🔍 *Health Claim Report*\n━━━━━━━━━━━━━━━━━━\n"
                f"🆔 `{escape_md(claim['claim_id'])}`\n"
                f"🛡 Policy: *{escape_md(claim.get('policy_name', 'N/A'))}*\n"
                f"📊 Status: `{escape_md(claim.get('status', 'N/A'))}`\n"
                f"{icd_str}"
                f"\n🤖 *Adjudication:*\n"
                f"• Outcome: *{escape_md(decision_val)}* ({confidence_val}%)\n"
                f"• Reasoning: {escape_md(summary_val)}\n\n"
                f"⚖️ *Policy Clauses Applied:*\n{escape_md(clauses_text)}"
            )
        else:
            est_cost = decision_data.get('estimated_cost', 0)
            approved = decision_data.get('approved_amount', 0)
            vehicle = claim.get('vehicle_type', 'Car')
            
            details = (
                f"🔍 *Automobile Claim Report*\n━━━━━━━━━━━━━━━━━━\n"
                f"🆔 `{escape_md(claim['claim_id'])}`\n"
                f"🛡 Policy: *{escape_md(claim.get('policy_name', 'N/A'))}*\n"
                f"📊 Status: `{escape_md(claim.get('status', 'N/A'))}`\n\n"
                f"🚗 *Vehicle Info:*\n"
                f"• Type: {escape_md(vehicle)}\n\n"
                f"💰 *Financials:*\n"
                f"• Est. Cost: ₹{est_cost}\n"
                f"• Approved: ₹{approved}\n\n"
                f"🤖 *Adjudication:*\n"
                f"• Outcome: *{escape_md(decision_val)}* ({confidence_val}%)\n"
                f"• Reasoning: {escape_md(summary_val)}\n\n"
                f"⚖️ *Policy Clauses Applied:*\n{escape_md(clauses_text)}"
            )

        markup = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="history"), InlineKeyboardButton("🏠 Menu", callback_data="back_main")]])

        if output_image and os.path.exists(output_image):
            await query.delete_message()
            await query.message.reply_photo(photo=open(output_image, 'rb'), caption=details, parse_mode="Markdown", reply_markup=markup)
        else:
            await query.edit_message_text(details, parse_mode="Markdown", reply_markup=markup)
        return

    if data == "health":
        session["claim_type"] = "health"
        session["state"] = State.HEALTH_CLAIM_MENU
        await query.edit_message_text("🏥 Health Claims", reply_markup=claim_menu())
        return
    if data == "auto":
        session["claim_type"] = "auto"
        session["state"] = State.AUTO_CLAIM_MENU
        await query.edit_message_text("🚗 Automobile Claims", reply_markup=claim_menu())
        return

    if data == "apply":
        session["docs"] = {}
        session["doc_index"] = 0
        if session["claim_type"] == "health":
            session["state"] = getattr(State, "ASK_HEALTH_ACCIDENT", "ASK_HEALTH_ACCIDENT")
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Yes", callback_data="accident_yes"), InlineKeyboardButton("❌ No", callback_data="accident_no")]
            ])
            await query.edit_message_text("🚑 *Was this an accident case?*", parse_mode="Markdown", reply_markup=markup)
        else:
            session["state"] = State.ASK_AUTO_DETAILS
            session["auto_details"] = {}
            session["auto_step"] = 0
            prompt = AUTO_FIELD_PROMPTS[AUTO_FIELDS_ORDER[0]]
            progress = progress_bar(0, len(AUTO_FIELDS_ORDER))
            # Initial prompt also gets the step counter
            step_count = f"Step 1/{len(AUTO_FIELDS_ORDER)}"
            await query.edit_message_text(f"📝 *{step_count}*: {prompt}\n{progress}", parse_mode="Markdown")
        return

    if data == "history":
        try:
            claims = get_claim_history(session["token"])["claims"]
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")
            return
        
        if not claims:
            await query.edit_message_text("📭 *No claims found.*", parse_mode="Markdown")
            return
        
        try:
            await query.edit_message_text("📂 *Your Claim History*", parse_mode="Markdown")
        except:
            await query.message.reply_text("📂 *Your Claim History*", parse_mode="Markdown")

        for c in claims:
            status = c.get('claim_status', c.get('status', 'N/A')).lower()
            icon = "🟢" if "approved" in status else "🔴" if "reject" in status or "denied" in status else "🟡"
            card_text = f"{icon} *{c['claim_type'].title()} Claim*\n🆔 `{escape_md(c['claim_id'])}`\n📅 {escape_md(c['created_at'][:10])}"
            await query.message.reply_text(card_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 Details", callback_data=f"claim_{c['claim_type']}_{c['claim_id']}")] ]))
        
        await query.message.reply_text("Next Action:", reply_markup=post_action_menu())
        return
    
    if data == "policies":
        policies = get_policies(session["token"])["policies"]
        msg = "📄 *Active Policies*\n\n" + "".join([f"🛡 *{p['policy_name']}*\n💰 Cover: ₹{p['coverage_amount']}\n\n" for p in policies])
        await query.edit_message_text(msg, parse_mode="Markdown")
        return
    
    if data == "back_main":
        session["state"] = State.MAIN_MENU
        try:
            await query.edit_message_text("Main Menu", reply_markup=main_menu())
        except:
            await query.message.reply_text("Main Menu", reply_markup=main_menu())
        return

# =========================
# HELPER: HEALTH UPLOAD TRIGGER
# =========================
async def trigger_next_health_upload(update_obj, session):
    docs_list = session.get("health_docs_list", list(HEALTH_DOCUMENTS))
    idx = session["doc_index"]
    
    if idx < len(docs_list):
        key, friendly_name = docs_list[idx]
        emoji = HEALTH_FILE_EMOJIS.get(key, "📄")
        
        progress = progress_bar(idx, len(docs_list))
        msg = (
            f"📎 *Upload Document {idx+1}/{len(docs_list)}*\n"
            f"{progress}\n\n"
            f"{emoji} {friendly_name}"
        )
        
        markup = None
        if key == "fir_receipt":
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("⏩ Skip FIR", callback_data="skip_fir")]])

        if hasattr(update_obj, "edit_message_text"):
            await update_obj.edit_message_text(msg, parse_mode="Markdown", reply_markup=markup)
        else:
            await update_obj.message.reply_text(msg, parse_mode="Markdown", reply_markup=markup)
    else:
        session["state"] = State.ASK_POLICY_NAME
        msg = "✅ All documents received.\n\n📜 *Enter Policy Name to submit:*"
        if hasattr(update_obj, "message") and update_obj.message:
             await update_obj.message.reply_text(msg, parse_mode="Markdown")
        elif hasattr(update_obj, "edit_message_text"):
             await update_obj.edit_message_text(msg, parse_mode="Markdown")

# =========================
# FILE & PHOTO HANDLER
# =========================

async def handle_attachment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session(update.effective_user.id)
    
    file_obj = None
    if update.message.document:
        file_obj = await update.message.document.get_file()
    elif update.message.photo:
        file_obj = await update.message.photo[-1].get_file()
    
    if not file_obj:
        return

    if session["state"] == State.UPLOADING_HEALTH_DOCS:
        docs_list = session.get("health_docs_list", list(HEALTH_DOCUMENTS))
        
        if session["doc_index"] < len(docs_list):
            key, _ = docs_list[session["doc_index"]]
            path = os.path.join(tempfile.gettempdir(), f"{key}.pdf")
            await file_obj.download_to_drive(path)
            session["docs"][key] = path
            
            session["doc_index"] += 1
            await trigger_next_health_upload(update, session)
        return

    if session["state"] == State.UPLOADING_AUTO_DOCS:
        path = os.path.join(tempfile.gettempdir(), "vehicle.jpg")
        await file_obj.download_to_drive(path)

        processing_msg = await update.message.reply_text("⏳ *Starting analysis...*", parse_mode="Markdown")
        await animate_processing(context, update.effective_chat.id, processing_msg.message_id)

        try:
            result = submit_automobile_claim(session["email"], session["token"], session["auto_details"], {"vehicle_image": path})
            formatted_msg = format_submission_report(result, claim_type="auto")
            output_image_path = result.get("output_image_path")

            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_msg.message_id)
            
            if output_image_path and os.path.exists(output_image_path):
                await update.message.reply_photo(photo=open(output_image_path, 'rb'), caption=formatted_msg, parse_mode="Markdown", reply_markup=post_action_menu())
            else:
                await update.message.reply_text(formatted_msg, parse_mode="Markdown", reply_markup=post_action_menu())
        except Exception as e:
            await update.message.reply_text(f"❌ Submission failed: {str(e)}")
            
        session["state"] = State.MAIN_MENU

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_attachment))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Telegram Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()