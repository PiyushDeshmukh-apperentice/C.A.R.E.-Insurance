import layoutparser as lp
import cv2
# help(lp)

image = cv2.imread("/mnt/StorageHDD/PICT/medical_report.png")
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
model = lp.EfficientDetLayoutModel("lp://PubLayNet/tf_efficientdet_d0/config")
layout = model.detect(image)
lp.draw_box(image, layout, box_width=3)

type(layout)
lp.elements.Layout
layout[0]

text_blocks = lp.Layout([b for b in layout if b.type=='Text'])
print(text_blocks)
figure_blocks = lp.Layout([b for b in layout if b.type=='Figure'])
print(figure_blocks)
text_blocks = lp.Layout([b for b in text_blocks \
                   if not any(b.is_in(b_fig) for b_fig in figure_blocks)])

h, w = image.shape[:2]

left_interval = lp.Interval(0, w/2*1.05, axis='x').put_on_canvas(image)

left_blocks = text_blocks.filter_by(left_interval, center=True)
left_blocks.sort(key = lambda b:b.coordinates[1], inplace=True)

right_blocks = lp.Layout([b for b in text_blocks if b not in left_blocks])
right_blocks.sort(key = lambda b:b.coordinates[1], inplace=True)

# And finally combine the two list and add the index
# according to the order
text_blocks = lp.Layout([b.set(id = idx) for idx, b in enumerate(left_blocks + right_blocks)])

lp.draw_box(image, text_blocks,
            box_width=3,
            show_element_id=True)

cv2.imwrite("medical_report_with_layout.png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

