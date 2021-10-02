--[[
    Name: toggle_dio_1hz.lua
    Desc: This example shows how to toggle DIO
    Note: This example requires firmware 1.0282 (T7) or 1.0023 (T4)
--]]

--print("Toggle the digital I/O called FIO3 (FIO5 on T4) at 1 Hz. Generates a 0.5Hz square wave.")

-- Assume the user is using a T7, toggle FIO3
local outpin = 2003
local dev_type = MB.readName("PRODUCT_ID")
local dev_name = MB.readName("DEVICE_NAME_DEFAULT")

--MB.W(6050, 0, 1) --suppress TRUNCATION ERROR --NEED FIRWARE 1.0028+

-- local dev_ = MB.readName("")
--[[
local dev_hw = MB.readName("HARDWARE_VERSION")
local dev_fw = MB.readName("FIRMWARE_VERSION")
local dev_hw_inst = MB.readName("HARDWARE_INSTALLED")
--local dev_eth = MB.readName("ETHERNET_MAC")
--local dev_eth = MB.R(6020, 98)
local dev_serial = MB.readName("SERIAL_NUMBER")
--]]

local counter = 0
print("dev_type: ", dev_type)
print("dev_name: ", dev_name)

--[[
print("dev_hw:", dev_hw)
print("dev_fw:", dev_fw)
print("dev_hw_inst:", dev_hw_inst)
--print("dev_eth:", dev_eth)
print("dev_serial:", dev_serial)
--]]

-- If the user is actually using a T4, toggle FIO5
if dev_type == 4 then
  outpin = 2005
end


local diostatus = 0
local sec = 5
-- Configure a 1000ms interval
LJ.IntervalConfig(0, 1000 * sec) -- 1000 ms = 1sec


function toggle_led(led_status)
  MB.W(outpin, 0, led_status)
end


toggle_led(1) --led on at start not after first CheckInterval


while true do
  -- If an interval is done
  if LJ.CheckInterval(0) then
    -- If the DIO pin is set high
    counter = counter + 1
    if diostatus == 1 then
      -- Set the DIO pin low
      diostatus = 0
      print(counter, outpin, diostatus, "low")
    else
      -- Set the DIO pin high
      diostatus = 1
      print(counter, outpin, diostatus, "high")
    end
    -- Apply the change to the DIO pin register (toggle on or off)
    --MB.W(outpin, 0, diostatus)
    toggle_led(diostatus) --now as function, also for call at start
  end
end
