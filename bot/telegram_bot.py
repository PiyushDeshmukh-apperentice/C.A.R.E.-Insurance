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
    "insurance": "🛡️"
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
    # (Same logic as before, kept clean)
    diagnosis_raw = result.get('diagnosis', 'N/A')
    diagnosis_str = "N/A"
    
    # Only show diagnosis if it's real data
    if isinstance(diagnosis_raw, dict) and diagnosis_raw.get('icd_code') not in [None, "N/A"]:
        diagnosis_str = f"{diagnosis_raw.get('icd_code')} - {diagnosis_raw.get('description', '')}"
    elif isinstance(diagnosis_raw, str) and len(diagnosis_raw) > 3 and "N/A" not in diagnosis_raw:
        diagnosis_str = diagnosis_raw

    reasons = result.get('decision_reasons', [])
    reasons_str = ", ".join(reasons) if reasons and isinstance(reasons[0], str) else \
                  "\n".join([f"• {r.get('description', str(r))}" for r in reasons]) if reasons else "None"

    clauses = result.get('applied_clauses', [])
    clauses_str = "\n".join([f"• {c.get('text', c.get('clause_text','Clause'))} (Pg {c.get('policy_page','?')})" for c in clauses]) if clauses and isinstance(clauses[0], dict) else "None"
    
    cost_str = ""
    if claim_type == "auto":
        breakdown = result.get('cost_breakdown', [])
        if breakdown:
            items = [f"• {i.get('part','Part')}: ₹{i.get('cost', i.get('estimated_cost',0))}" for i in breakdown]
            cost_str = "\n📋 *Cost Breakdown:*\n" + "\n".join(items)

    msg = (
        f"✅ *{claim_type.title()} Claim Submitted*\n━━━━━━━━━━━━━━━━━━\n"
        f"🆔 *ID:* `{escape_md(result['claim_id'])}`\n"
        f"📌 *Decision:* {escape_md(result['decision'])}\n"
        f"📊 *Confidence:* {result['confidence']}%\n\n"
    )
    
    # Only show diagnosis if it exists
    if claim_type == "health" and diagnosis_str != "N/A":
        msg += f"🔍 *Diagnosis:* {escape_md(diagnosis_str)}\n"
    elif claim_type == "auto":
        msg += f"💰 *Est. Cost:* ₹{result.get('estimated_cost', 0)}\n{escape_md(cost_str)}\n"

    msg += (
        f"\n📝 *Summary:*\n_{escape_md(result['summary'])}_\n\n"
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
    banner_url = "https://img.freepik.com/free-vector/chatbot-artificial-intelligence-abstract-concept-illustration_335657-3723.jpg"
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

        # --- FIX 1: Input Normalization ---
        # Normalize Boolean inputs (Yes/No)
        if current_field in ["licensed", "under_influence"]:
            if text.lower() in ["yes", "y"]: value_to_save = True
            elif text.lower() in ["no", "n"]: value_to_save = False
            else:
                await update.message.reply_text("⚠️ Please answer with 'Yes' or 'No'.")
                return
        
        # Normalize Gender
        if current_field == "driver_gender":
            val = text.lower()
            if val not in ["male", "female", "other"]:
                await update.message.reply_text("⚠️ Please enter Male, Female, or Other.")
                return
            value_to_save = val

        # Normalize Activity (Road Accident -> road_accident)
        if current_field == "activity":
            value_to_save = text.lower().replace(" ", "_")

        session["auto_details"][current_field] = value_to_save
        session["auto_step"] += 1

        if session["auto_step"] < len(AUTO_FIELDS_ORDER):
            next_field = AUTO_FIELDS_ORDER[session["auto_step"]]
            prompt = AUTO_FIELD_PROMPTS.get(next_field, f"Enter {next_field}:")
            progress = progress_bar(session["auto_step"], len(AUTO_FIELDS_ORDER))
            await update.message.reply_text(f"{prompt}\n{progress}")
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

    if data.startswith("claim_"):
        parts = data.split("_")
        claim_type = parts[1]
        claim_id = "_".join(parts[2:])
        try:
            claim = get_claim_details(session["token"], claim_id, claim_type)
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")
            return

        # --- FIX 2: Cleaner Data Display ---
        decision_data = claim.get('decision', {}) if isinstance(claim.get('decision'), dict) else {}
        decision_val = decision_data.get('decision', claim.get('decision', 'N/A'))
        confidence_val = decision_data.get('confidence', 'N/A')
        summary_val = decision_data.get('reason', 'No summary available')
        clauses_text = "\n".join([f"• {c.get('clause_text', 'N/A')} (Pg {c.get('policy_page', 'N/A')})" for c in claim.get('applied_clauses', [])]) or "None"

        details = ""
        output_image = claim.get('output_image_path') if claim_type == "auto" else None

        if claim_type == "health":
            diagnosis = decision_data.get('diagnosis', {})
            # Only extract ICD if it exists and isn't N/A
            icd_str = ""
            if isinstance(diagnosis, dict) and diagnosis.get('icd_code') not in [None, "N/A"]:
                icd_str = f"\n🏥 *Diagnosis:*\nICD: `{escape_md(diagnosis['icd_code'])}`\n"

            # Cleaned up view: Removed Hospital Info, Conditional Diagnosis
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
            session["state"] = State.UPLOADING_HEALTH_DOCS
            
            # Smart Health Upload UI
            key, _ = HEALTH_DOCUMENTS[0]
            emoji = HEALTH_FILE_EMOJIS.get(key, "📄")
            friendly_name = key.replace("_", " ").title()
            
            progress = progress_bar(0, len(HEALTH_DOCUMENTS))
            msg = (
                f"📎 *Upload Document 1/{len(HEALTH_DOCUMENTS)}*\n"
                f"{progress}\n\n"
                f"{emoji} Please upload your *{friendly_name}*."
            )
            await query.edit_message_text(msg, parse_mode="Markdown")
        else:
            session["state"] = State.ASK_AUTO_DETAILS
            session["auto_details"] = {}
            session["auto_step"] = 0
            prompt = AUTO_FIELD_PROMPTS[AUTO_FIELDS_ORDER[0]]
            progress = progress_bar(0, len(AUTO_FIELDS_ORDER))
            await query.edit_message_text(f"{prompt}\n{progress}")
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
        key, _ = HEALTH_DOCUMENTS[session["doc_index"]]
        path = os.path.join(tempfile.gettempdir(), f"{key}.pdf")
        await file_obj.download_to_drive(path)
        session["docs"][key] = path
        session["doc_index"] += 1
        
        if session["doc_index"] < len(HEALTH_DOCUMENTS):
            next_key, _ = HEALTH_DOCUMENTS[session["doc_index"]]
            emoji = HEALTH_FILE_EMOJIS.get(next_key, "📄")
            friendly_name = next_key.replace("_", " ").title()
            
            progress = progress_bar(session["doc_index"], len(HEALTH_DOCUMENTS))
            msg = (
                f"✅ Received.\n\n"
                f"📎 *Upload Document {session['doc_index']+1}/{len(HEALTH_DOCUMENTS)}*\n"
                f"{progress}\n\n"
                f"{emoji} Please upload your *{friendly_name}*."
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            session["state"] = State.ASK_POLICY_NAME
            await update.message.reply_text("✅ All documents received.\n\n📜 *Enter Policy Name to submit:*", parse_mode="Markdown")
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