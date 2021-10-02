print("read voltage from potentiometer via XXX and set same voltage to YYY")

local InputVoltage = 0

LJ.IntervalConfig(0, 1000 * 0.1 * 1) -- 100ms = 0.1sec

local check_interval = LJ.CheckInterval
local mb_read = MB.R
local mb_write = MB.W

local voltage_warning = false

function check_voltage(v)
  if v > 2.5 then
    voltage_warning = true
  end
end

while true do
  if check_interval(0) then
    --ADDRESS 0 -> AIN0 -> 0 / type 3  --> float
    --InputVoltage = mb_read(0, 3)

    --ADDRESS 6 -> AIN1 -> 2
    --InputVoltage = mb_read(2, 3)
    
    --ADDRESS 6 -> AIN6 via FIO6 -> 12
    InputVoltage = mb_read(12, 3)
    
    --set read voltage to DAC0 -> 1000
    --mb_write(1000, 3, InputVoltage)
    
    --DAC1 -> red_led + multimeter_verification
    --set read voltage to DAC1 -> 1002
    mb_write(1002, 3, InputVoltage)
    
    --COMBO / read AIN6 and write to DAC1
    --mb_write(1002, 3, mb_read(12, 3))
    --MB.writeName("DAC1", MB.readName("AIN6"))
    
    check_voltage(InputVoltage)
    
    print("in -> AIN6: ", InputVoltage, 
      " / out <- DAC1 ", mb_read(1002, 3), 
      "voltage_warning: ", voltage_warning)
    
    --print("AIN. ", InputVoltage)
    --print("AIN. ", MB.readName("AIN6"))
  end
end
