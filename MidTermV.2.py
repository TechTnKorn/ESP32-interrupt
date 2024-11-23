from machine import Pin, SoftI2C, Timer
import ssd1306_2, framebuf, images , time
i2c = SoftI2C(scl=Pin(22), sda=Pin(21)) # ESP32 Pin assignment
width = 128 # Width size of display
height = 64 # Height size of display
display = ssd1306_2.SSD1306_I2C(width, height, i2c) # Initialize display ssd1306
led = Pin(2,Pin.OUT) # create output pin on GPIO2
tim0 = Timer(0) # SwitchMode's timer
tim1 = Timer(1) # LED ON's timer
tim2 = Timer(2) # LED OFF's timer
tim3 = Timer(3) # IMG's timer
mode = 1 # Mode
sub_mode = 0 # initialize sub_mode
btn_flag = 0 # initialize btn_flag
btn_press = 0 # initialize btn_press
buffer = images.logo # initialize buffer
led.value(0) # LED OFF
buttn = Pin(13,Pin.IN,Pin.PULL_UP) # create input pin on GPIO13 //

def switchMode(pin): #ฟังก์ชั่นสำหรับการเปลี่ยนโหมด
    global mode,sub_mode, btn_press, buffer #นำตัวแปรเข้ามาในฟังก์ชั่น
    if btn_press == 1 and pin.value() == 0: #ถ้ากดปุ่ม1ที และยังคงกดอยู่เป็นเวลา2วินาที
        if mode == 1: #ถ้าเป็นmode 1 
            mode = 2 #เปลี่ยนmodeเป้น2
        else: #ถ้าเป็นmode 2 
            mode = 1 #เปลี่ยนmodeเป้น1
            sub_mode = 0 #เปลี่ยนsub modeเป้น 0(เริ่มต้น)
    else:#ถ้ากดปุ่มมาก1ที ภายในเวลา2วิ
        if mode == 2: #ถ้าอยู่ในmode 2
            sub_mode = btn_press #นำจำนวนการกด(มีค่าไม่เกิน3)มาเป็นsub mode
            tim1.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:led.value(led.value()^1)) #จับเวลา การกระพริบของled 1วินาที
            tim2.init(period=2000*sub_mode, mode=Timer.ONE_SHOT, callback=lambda t:LED_OFF()) #จับเวลา การดับของled ขึ้นอยู่กับ sub mode โดยเรียกใช้ฟังก์ชั่น LED_OFF
            if sub_mode == 1: # sub mode 1 (mode 2.1)
                tim3.init(period=555, mode=Timer.PERIODIC, callback=lambda t:switchIMG()) #choice B
            elif sub_mode == 2: # sub mode 2 (mode 2.2)
                tim3.deinit() #หยุดการเปลี่ยนรูปภาพ
                buffer = images.logo #choice A
            elif sub_mode == 3: # sub mode 3 (mode 2.3)
                tim3.init(period=555, mode=Timer.PERIODIC, callback=lambda t:switchIMG()) #choice  C
    btn_press = 0 #เปลี่ยนจำนวนการกดเป็นค่าเริ่มต้น
    
def countDown(pin): #ตัวจับเวลาการกดปุ่ม
    global btn_flag, mode, btn_press #นำตัวแปรเข้ามาในฟังก์ชั่น
    if pin.value() == 0 and btn_flag == 0: #ถ้ากดปุ่มและflagเป็น 0
        btn_flag = 1 #เปลี่ยนค่าflagเป็น 1
        if btn_press < 3: #ถ้ากดปุ่มยังน้อยกว่า3ครั้ง
            btn_press += 1 #เพิ่มจำนวนการกดปุ่ม1ครั้ง
        if btn_press == 1: #ถ้ากดปุ่มในรอบแรก
            tim0.init(period=2000, mode=Timer.ONE_SHOT, callback=lambda t:switchMode(pin)) #จับเวลาการเปลี่ยนmodeโดยใช้ฟังก์ชั่นswitchMode
    else: #ถ้าไม่ได้กดปุ่มและflagเป็น 1
        btn_flag = 0 #เปลี่ยนค่าflagเป็น 0
    
def switchIMG(): #ฟังก์ชั่นการเปลี่ยนรูป
    global buffer #นำตัวแปรเข้ามาในฟังก์ชั่น
    if buffer == images.images_list[0]: #ถ้ารูปเป็นindexที่0 //
        buffer = images.images_list[1] # เปลี่ยนเป็นรูปที่indexที่ 1 //
    else: #ถ้ารูปเป็นindexที่1
        buffer = images.images_list[0] # เปลี่ยนเป็นรูปที่indexที่ 0 //

def LED_OFF(): # ฟังก์ชั่นปิดไฟLED
    global sub_mode #นำตัวแปรเข้ามาในฟังก์ชั่น
    tim1.deinit() #หยุดการกระพริบของไฟ
    if sub_mode == 3: #ถ้าเป็นsub mode 3(mode 2.3)
        tim1.init(period=500, mode=Timer.PERIODIC, callback=lambda t:led.value(led.value()^1))#C
    
buttn.irq(trigger= Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=countDown) # Attach an interrupt to that pin by calling the irq() method

while 1: #OLED dispaly
    if sub_mode == 0: #ถ้าเป็นsub mode 0(mode 2.0)
        display.fill(0) #เคลียร์หน้าจอ
        display.text(f'Mode: {mode}', 5, 20) # กำหนดข้อความและตำแหน่ง //
        display.text(f'image Mode: {mode}' + "." + str(sub_mode), 0, 40) # กำหนดข้อความและตำแหน่ง //
        display.rect(0,0,width,height,1) # กำหนดกรอบ
    else: #ถ้าเป็นsub mode 1 2 3(mode 2.1 2.2 2.3)
        image = framebuf.FrameBuffer(buffer,width,height,framebuf.MONO_HLSB) # กำหนดรูป //
        display.fill(0) # fill entire screen with color=0
        display.blit(image, 0, 0) # Draw image
    display.show() # display

        

