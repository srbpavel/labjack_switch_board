-- Use USER_RAM0_U16 (register 46180) to determine which control loop to run
                    local ramval = 0
                    MB.W(46180, 0, ramval)
                    local loop0 = 0
                    local loop1 = 1
                    local loop2 = 2
                    -- Setup an interval to control loop execution speed. Update every second
                    LJ.IntervalConfig(0,1000)
                    while true do
                      if LJ.CheckInterval(0) then
                        ramval = MB.R(46180, 0)
                        if ramval == loop0 then
                          print("using loop0")
                        end
                        if ramval == loop1 then
                          print("using loop1")
                        end
                        if ramval == loop2 then
                          print("using loop2")
                        end
                      end
                  end
                  