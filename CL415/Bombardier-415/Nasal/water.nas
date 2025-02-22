Wstart = func {
  setprop("/controls/armament/trigger", 1);
}

Wstop = func {
  setprop("/controls/armament/trigger", 0); 
}

var flash_trigger = props.globals.getNode("controls/armament/trigger", 0);
