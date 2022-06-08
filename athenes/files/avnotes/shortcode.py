__all__ = ['shortcode']

# Don't look below, you will not understand this Python code :) I don't.

from js2py.pyjs import *
# setting scope
var = Scope( JS_BUILTINS )
set_global_object(var)

# Code follows:
var.registers(['decodeShortCode', 'interleave', 'makeShortCode'])
@Js
def PyJsHoisted_makeShortCode_(lat, lon, zoom, this, arguments, var=var):
    var = Scope({'lat':lat, 'lon':lon, 'zoom':zoom, 'this':this, 'arguments':arguments}, var)
    var.registers(['lon', 'c2', 'i', 'str', 'x', 'zoom', 'lat', 'c1', 'y'])
    var.put('char_array', Js('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_~'))
    var.put('x', var.get('Math').callprop('round', ((var.get('lon')+Js(180.0))*((Js(1.0)<<Js(30.0))/Js(90.0)))))
    var.put('y', var.get('Math').callprop('round', ((var.get('lat')+Js(90.0))*((Js(1.0)<<Js(30.0))/Js(45.0)))))
    var.put('str', Js(''))
    var.put('c1', var.get('interleave')(PyJsBshift(var.get('x'),Js(17.0)), PyJsBshift(var.get('y'),Js(17.0))))
    var.put('c2', var.get('interleave')((PyJsBshift(var.get('x'),Js(2.0))&Js(32767)), (PyJsBshift(var.get('y'),Js(2.0))&Js(32767))))
    #for JS loop
    var.put('i', Js(0.0))
    while ((var.get('i')<var.get('Math').callprop('ceil', ((var.get('zoom')+Js(8.0))/Js(3.0)))) and (var.get('i')<Js(5.0))):
        try:
            var.put('digit', ((var.get('c1')>>(Js(24.0)-(Js(6.0)*var.get('i'))))&Js(63)))
            var.put('str', var.get('char_array').callprop('charAt', var.get('digit')), '+')
        finally:
                var.put('i',Js(var.get('i').to_number())+Js(1))
    #for JS loop
    var.put('i', Js(5.0))
    while (var.get('i')<var.get('Math').callprop('ceil', ((var.get('zoom')+Js(8.0))/Js(3.0)))):
        try:
            var.put('digit', ((var.get('c2')>>(Js(24.0)-(Js(6.0)*(var.get('i')-Js(5.0)))))&Js(63)))
            var.put('str', var.get('char_array').callprop('charAt', var.get('digit')), '+')
        finally:
                var.put('i',Js(var.get('i').to_number())+Js(1))
    #for JS loop
    var.put('i', Js(0.0))
    while (var.get('i')<((var.get('zoom')+Js(8.0))%Js(3.0))):
        try:
            var.put('str', Js('-'), '+')
        finally:
                var.put('i',Js(var.get('i').to_number())+Js(1))
    return var.get('str')
PyJsHoisted_makeShortCode_.func_name = 'makeShortCode'
var.put('makeShortCode', PyJsHoisted_makeShortCode_)
@Js
def PyJsHoisted_interleave_(x, y, this, arguments, var=var):
    var = Scope({'x':x, 'y':y, 'this':this, 'arguments':arguments}, var)
    var.registers(['x', 'y'])
    var.put('x', ((var.get('x')|(var.get('x')<<Js(8.0)))&Js(16711935)))
    var.put('x', ((var.get('x')|(var.get('x')<<Js(4.0)))&Js(252645135)))
    var.put('x', ((var.get('x')|(var.get('x')<<Js(2.0)))&Js(858993459)))
    var.put('x', ((var.get('x')|(var.get('x')<<Js(1.0)))&Js(1431655765)))
    var.put('y', ((var.get('y')|(var.get('y')<<Js(8.0)))&Js(16711935)))
    var.put('y', ((var.get('y')|(var.get('y')<<Js(4.0)))&Js(252645135)))
    var.put('y', ((var.get('y')|(var.get('y')<<Js(2.0)))&Js(858993459)))
    var.put('y', ((var.get('y')|(var.get('y')<<Js(1.0)))&Js(1431655765)))
    return ((var.get('x')<<Js(1.0))|var.get('y'))
PyJsHoisted_interleave_.func_name = 'interleave'
var.put('interleave', PyJsHoisted_interleave_)
@Js
def PyJsHoisted_decodeShortCode_(sc, this, arguments, var=var):
    var = Scope({'sc':sc, 'this':this, 'arguments':arguments}, var)
    var.registers(['sc', 'i', 'x', 'z', 'y'])
    var.put('char_array', Js('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_~'))
    var.put('i', Js(0.0))
    var.put('x', Js(0.0))
    var.put('y', Js(0.0))
    var.put('z', (-Js(8.0)))
    #for JS loop
    var.put('i', Js(0.0))
    while (var.get('i')<var.get('sc').get('length')):
        try:
            var.put('ch', var.get('sc').callprop('charAt', var.get('i')))
            var.put('digit', var.get('char_array').callprop('indexOf', var.get('ch')))
            if (var.get('digit')==(-Js(1.0))):
                break
            var.put('x', Js(3.0), '<<')
            var.put('y', Js(3.0), '<<')
            #for JS loop
            var.put('j', Js(2.0))
            while (var.get('j')>=Js(0.0)):
                try:
                    var.put('x', (Js(0.0) if ((var.get('digit')&(Js(1.0)<<((var.get('j')+var.get('j'))+Js(1.0))))==Js(0.0)) else (Js(1.0)<<var.get('j'))), '|')
                    var.put('y', (Js(0.0) if ((var.get('digit')&(Js(1.0)<<(var.get('j')+var.get('j'))))==Js(0.0)) else (Js(1.0)<<var.get('j'))), '|')
                finally:
                        (var.put('j',Js(var.get('j').to_number())-Js(1))+Js(1))
            var.put('z', Js(3.0), '+')
        finally:
                (var.put('i',Js(var.get('i').to_number())+Js(1))-Js(1))
    var.put('x', (((var.get('x')*var.get('Math').callprop('pow', Js(2.0), (Js(2.0)-(Js(3.0)*var.get('i')))))*Js(90.0))-Js(180.0)))
    var.put('y', (((var.get('y')*var.get('Math').callprop('pow', Js(2.0), (Js(2.0)-(Js(3.0)*var.get('i')))))*Js(45.0))-Js(90.0)))
    if ((var.get('i')<var.get('sc').get('length')) and (var.get('sc').callprop('charAt', var.get('i'))==Js('-'))):
        var.put('z', Js(2.0), '-')
        if (((var.get('i')+Js(1.0))<var.get('sc').get('length')) and (var.get('sc').callprop('charAt', (var.get('i')+Js(1.0)))==Js('-'))):
            (var.put('z',Js(var.get('z').to_number())+Js(1))-Js(1))
    return var.get('Array').create(var.get('y'), var.get('x'), var.get('z'))
PyJsHoisted_decodeShortCode_.func_name = 'decodeShortCode'
var.put('decodeShortCode', PyJsHoisted_decodeShortCode_)
pass
pass
pass
pass


# Add lib to the module scope
shortcode = var.to_python()