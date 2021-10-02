--print("Read and display the device temperature at 0.5 Hz.")
local tempK = 0
local tempF = 0
local const_kelvin = 273.15
local tempK_via_name = 0 -- nektery define predem, nektery ne ? 

MB.W(48005, 0, 1)                   --Ensure analog is on

LJ.IntervalConfig(0, 500 * 2)           --Configure interval
local checkInterval=LJ.CheckInterval

function ConvertToF(degK)
  local degF = 0
  degF = (degK - 273.15) * 1.8000 + 32.00
  return degF
end

function Convert_to_celsius(degK)
  local degC = 0
  degC = (degK - const_kelvin)
  return degC
end

while true do
  if checkInterval(0) then     --interval finished
    tempK = MB.R(60052, 3)       --read address 60052 TEMPERATURE_DEVICE_K, type is 3
    --[[tempK_via_name = MB.readName("TEMPERATURE_DEVICE_K")
    tempC_via_name = Convert_to_celsius(tempK_via_name)
    tempF = ConvertToF(tempK)
    --]]
    tempC = Convert_to_celsius(tempK)
    print(tempC, "°C")
    --print(tempC, "°C /", tempK_via_name, tempC_via_name)
    --print(tempF, "°F")
  end
end