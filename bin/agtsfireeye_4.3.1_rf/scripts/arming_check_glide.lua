-- This script runs a custom arming check to make sure the aircraft is not
-- configured for gliding, in case this has been done previously during an
-- engine-out emergency.

local auth_id = arming:get_aux_auth_id()

-- bind a parameter to a variable
function bind_param(name)
  local p = Parameter()
  assert(p:init(name), string.format('could not find %s parameter', name))
  return p
end

local TECS_SPDWEIGHT = bind_param("TECS_SPDWEIGHT")

function update() -- this is the loop which periodically runs
  if auth_id then
    if TECS_SPDWEIGHT:get() > 1.95 then
      arming:set_aux_auth_failed(auth_id, "TECS set for glide")
    else
      arming:set_aux_auth_passed(auth_id)
    end
  end
  return update, 2000 -- reschedules the loop in 2 seconds
end

return update() -- run immediately before starting to reschedule
