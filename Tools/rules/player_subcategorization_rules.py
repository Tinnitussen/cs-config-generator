"""
Player subcategorization rules for command classification.
"""

def get_player_subcategory(command: dict) -> str:
    """
    Determines the subcategory of a player command based on a set of rules.
    The rules are processed in order, and the first match wins.
    """
    cmd_name = command.get('command', '')
    ui_type = command.get('uiData', {}).get('type')
    flags = command.get('consoleData', {}).get('flags', [])
    description = command.get('consoleData', {}).get('description', '').lower()

    # Manual override check
    manual_category = command.get('uiData', {}).get('manual_category')
    if manual_category and '/' in manual_category:
        return manual_category.split('/')[1]

    # --- Crosshair ---
    if cmd_name.startswith(('cl_crosshair', 'crosshair', 'cl_fixedcrosshairgap', 'cl_ironsight_usecrosshaircolor')):
        return "crosshair"

    # --- Viewmodel & FOV ---
    if cmd_name.startswith(('viewmodel_', 'cl_bob', 'fov_', 'c_', 'cam_')) or cmd_name == 'cl_righthand':
        return "viewmodel"

    # --- HUD ---
    if (cmd_name.startswith(('hud_', 'cl_hud', 'ui_', 'panorama_', 'cl_teamcounter_', 'cl_teamid_overhead_')) or
        cmd_name in ['cl_showloadout', 'cl_show_clan_in_death_notice', 'cl_draw_only_deathnotices',
                     'safezonex', 'safezoney', 'cl_teammate_colors_show', 'cl_deathnotices_show_numbers',
                     'cl_show_equipped_character_for_player_avatars', 'cl_hide_avatar_images',
                     'cl_allow_animated_avatars', 'cl_scoreboard_survivors_always_on',
                     'cl_weapon_selection_rarity_color', 'mapoverview_icon_scale']):
        return "hud"

    # --- Radar ---
    if cmd_name.startswith(('cl_radar', 'radar_')):
        return "radar"

    # --- Input ---
    if (cmd_name.startswith(('input_', 'm_', 'joy_', 'key_')) or
        cmd_name in ['bind', 'unbind', 'unbindall', 'alias', 'cl_mouselook',
                     'sensitivity', 'zoom_sensitivity_ratio', 'cl_input_enable_raw_keyboard',
                     'input_button_code_is_scan_code_scd', 'joystick']):
        return "input"

    # --- Gameplay ---
    if (cmd_name.startswith(('gameplay_', 'option_', 'cl_buy', 'cl_rebuy', 'cl_autobuy', 'violence_')) or
        cmd_name in ['cl_autowepswitch', 'cl_dm_buyrandomweapons', 'cl_use_opens_buy_menu',
                     'cl_debounce_zoom', 'cl_silencer_mode', 'cl_autohelp', 'autobuy', 'rebuy',
                     'cl_color', 'cl_join_advertise', 'cl_playerspraydisable',
                     'cl_sniper_auto_rezoom', 'cl_sniper_delay_unscope', 'cl_prefer_lefthanded',
                     'switchhands', 'switchhandsleft', 'switchhandsright', 'lastinv', 'invnext', 'invprev', 'battery_saver']):
        return "gameplay"

    # --- Audio ---
    if (cmd_name.startswith(('snd_', 'sound_', 'voice_', 'dsp_', 'cc_')) or
        'sound' in description or 'audio' in description or
        cmd_name in ['volume', 'closecaption', 'soundinfo', 'speaker_config']):
        return "audio"

    # --- Communication ---
    if (cmd_name.startswith(('comm_', 'chat_', 'radio')) or 'chat' in description or
        cmd_name.startswith(('cl_mute', 'cl_radial_')) or
        cmd_name in ['cl_clutch_mode', 'clutch_mode_toggle', 'cl_sanitize_player_names']):
        return "communication"

    # --- Network ---
    if cmd_name.startswith('net_') or cmd_name in [
        'cl_timeout', 'cl_resend', 'rate', 'disconnect', 'connect', 'password',
        'cl_interp', 'cl_interp_ratio', 'cl_clock_correction'
    ]:
        return "network"

    # --- Developer/Spectator ---
    # This is more specific than rendering/debugging, so check first.
    if cmd_name.startswith(('spec_', 'tv_', 'demo_')) or cmd_name in ['demoui', 'playdemo', 'record', 'stop', 'gotv_theater_container']:
        return "developer/spectator"

    # --- Developer/Rendering ---
    if cmd_name.startswith(('r_', 'mat_', 'gl_', 'csm_', 'fog_')) or 'render' in description or 'graphic' in description:
        return "developer/rendering"

    # --- Developer/Debugging ---
    if (cmd_name.startswith(('debug_', 'dev_', 'cl_ent_', 'cl_phys_', 'cl_show', 'cl_debug', 'phys_', 'annotation_', 'adsp_debug', 'bug_submitter_')) or
        cmd_name in ['pwatchent', 'pwatchvar', 'getpos', 'getpos_exact', 'cl_pclass',
                     'cl_pdump', 'cl_showerror', 'con_enable'] or 'debug' in description):
        return "developer/debugging"

    # --- Actions ---
    # Captures commands like +attack, -attack, slot*, etc.
    if (ui_type == 'action'):
        # Check if it's a simple command without arguments, often used for binds
        is_simple_action = ' ' not in cmd_name and not cmd_name.startswith('_')
        # Check if it's a bindable action like +jump
        is_bindable_action = cmd_name.startswith(('+', '-'))

        if is_simple_action or is_bindable_action:
            # Exclude commands that are actions but better suited for other categories
            if cmd_name not in ['bind', 'unbind', 'unbindall', 'alias', 'disconnect', 'connect', 'demoui', 'playdemo', 'record', 'stop', 'quit']:
                 return "actions"

    # --- Cheats ---
    # Catch-all for cheat-flagged commands not caught by more specific rules.
    if 'cheat' in flags:
        return "cheats"

    # --- Misc ---
    return "misc"
