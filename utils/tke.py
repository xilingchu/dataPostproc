import re

#-----------------------------------------#
#------- Sort The Name Of Variable -------#
#-----------------------------------------#
def _sortName(var):
    '''
    Sort the variable in order u,v,w
    For example: vwu ----> uvw
    '''
    type = re.compile(r'[uvw][^uvw]?')
    var_out = ''
    var_list = type.findall(var)
    var_list.sort()     # Sort it to get right order of variable
    if len(var_list) == 3 and var_list[1] == var_list[2]:
        var_list.append(var_list.pop(0))
    for var in var_list:
        var_out += var
    return var_out
    
#----------------------------------------#
#- Define Turbulent Kinetic Energy Name -#
#----------------------------------------#
def _defTKEName(varname):
    # This code defines the name of kinetic
    # energy.
    vardict = {}
    direction = {'u': 'x', 'v':'y', 'w':'z'}
    varname = _sortName(varname)
    ui, uj = varname[0], varname[1]
    #-------------- Production --------------#
    i = 0
    if ui == uj:
        for dire_var, dire in direction.items():
            i += 1
            vardict['prod_{}'.format(i)] = 'm2{}d{}d{}'.format(_sortName(ui+dire_var), uj, dire)
    else:
        for dire_var, dire in direction.items():
            i += 1
            vardict['prod_{}'.format(i)] = 'm{}d{}d{}'.format(_sortName(ui+dire_var), uj, dire)
        for dire_var, dire in direction.items():
            i += 1
            vardict['prod_{}'.format(i)] = 'm{}d{}d{}'.format(_sortName(uj+dire_var), ui, dire)
    #---------- Turbulent Transport ----------#
    i = 0
    for dire_var, dire in direction.items():
        i += 1
        vardict['turb_trans_{}'.format(i)] = 'md{}d{}'.format(ui+uj+dire_var, dire)
    #----------- Viscous Transport -----------#
    i = 0
    for dire_var, dire in direction.items():
        i += 1
        vardict['visc_trans_{}'.format(i)] = 'd2{}d{}2'.format(_sortName(ui+uj), dire)
    #-- Pressure Strain&Pressure Transport --#
    if ui == uj:
        vardict['press_strain'] = '2pd{}d{}'.format(ui, direction[uj])
        vardict['press_trans'] = '2dp{}d{}'.format(ui, direction[uj])
    else:
        vardict['press_strain'] = 'p(d{}d{}+d{}d{})'.format(ui, direction[uj], uj, direction[ui])
        vardict['press_trans'] = 'dp{}d{}+dp{}d{}'.format(ui, direction[uj], uj, direction[ui])
    #---------- Viscous Dissipation ----------#
    i = 0
    for dire_var, dire in direction.items():
        i += 1
        vardict['visc_diss_{}'.format(i)] = '2d{}d{}d{}d{}'.format(ui, dire, uj, dire)
    return vardict
