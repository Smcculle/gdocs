# := unknown abbreviations
_MAPPINGS = {
    "ty": "type",
    "st": "style_type",
    "s": "string",
    "ibi": "insert_before_index",
    "si": "starting_index",
    "ei": "ending_index",
    "is": "insert",
    "ds": "delete",
    "as": "adjust_style",
    "fm": "?fm", #
    "timestamp": "timestamp",
    "UID": "UID",
    "rev": "rev",
    "SID": "SID",
    "SRev": "SRev",
    "sm": "style_modification",
    "mts": "multiset",
    "sugid": "suggestion_id",
    "tbs_al": "?table_alignment", #
    "tbs_of": "?table_offset", #
    "das_a": "datasheet_anchor",
    "ps_ltr": "?ps_ltr", #
    "hs_nt": "heading_style_normal_text", 
    "ds_pw": "page_width",
    "ds_ph": "page_height",
    "ds_mb": "margin_bottom",
    "ds_ml": "margin_left",
    "ds_mt": "margin_top",
    "ds_mr": "margin_right",
    "snapshot": "snapshot",
    "lgs_l": "language",
    "hs_h1": "heading_style_one",
    "hs_h2": "heading_style_two",
    "hs_h3": "heading_style_three",
    "hs_h4": "heading_style_four",
    "hs_h5": "heading_style_five",
    "hs_h6": "heading_style_six",
    "hs_st": "heading_style_subtitle",
    "hs_t": "heading_style_title",
    "sdef_ps": "set_default_paragraph_style",
    "sdef_ts": "set_default_text_style",
    "ts_bd": "bold",
    "ts_bd_i": "bold_flag",
    "ts_bgc": "background_color",
    "ts_bgc_i": "background_color_flag",
    "ts_ff": "font_family",
    "ts_ff_i": "font_family_flag",
    "ts_fgc": "foreground_color",
    "ts_fgc_i": "foreground_color_flag",
    "ts_fs": "font_size",
    "ts_fs_i": "font_size_flag",
    "ts_it": "italic",
    "ts_it_i": "italic_flag",
    "ts_sc": "?ts_sc", #
    "ts_sc_i": "?ts_sc_flag", #
    "ts_st": "strikethrough",
    "ts_st_i": "strikethrough_flag",
    "ts_un": "underline",
    "ts_un_i": "underline_flag",
    "ts_va": "vertical_align",
    "ts_va_i": "vertical_align_flag",
    "ps_al": "alignment",
    "ps_al_i": "alignment_flag",
    "ps_awao": "?ps_awao", #
    "ps_awao_i": "?ps_awao_flag", #
    "ps_hd": "heading_style",
    "ps_hdid": "heading_id",
    "ps_ifl": "indent_first_line",
    "ps_ifl_i": "indent_first_line_flag",
    "ps_il": "indent_line",
    "ps_il_i": "indent_line_flag",
    "ps_ir": "?ps_ir", #
    "ps_ir_i": "?ps_ir_flag", #
    "ps_klt": "?ps_klt", #
    "ps_klt_i": "?ps_klt_flag", #
    "ps_kwn": "?ps_kwn", #
    "ps_kwn_i": "?ps_kwn_flag", #
    "ps_ls": "line_space",
    "ps_ls_i": "line_space_flag",
    "ps_sa": "space_after_paragraph",
    "ps_sa_i": "space_after_paragraph_flag",
    "ps_sb": "space_before_paragraph",
    "ps_sb_i": "space_before_paragraph_flag",
    "ps_sm": "?ps_sm", #
    "ps_sm_i": "?ps_sm_flag", #
    "ps_ts": "?ps_ts", #
    "cv": "?cv", #
    "opValue": "opValue",
    "op": "op",
    "opIndex": "opIndex",
    "ds_hi": "?ds_hi", #
    "sugid": "suggestion_id",
    "id": "id",
    
    #mostly related to insertion of kix objects in page
    "ls_nest": "?ls_nest", #
    "spi": "?spi", #
    "epm": "?epm", #
    "ae": "?ae", #
    "ue": "?ue", #
    "epm": "?epm", #
    "et": "?et",  #
    "ls_ts": "?ls_ts", #
    "ls_id": "?ls_id", #
    "ee_eo": "?ee_eo", #
    "le_nb": "?le_nb", #
    "hfe_hft": "?hfe_hft", #
    }

def remap(old_key):
    return _MAPPINGS[old_key]

def load_keys():
    with open('keys.txt', 'r') as f:
        key_data = f.read()
        for key in key_data.split('\n'):
            _MAPPINGS[key] = key

load_keys()
                



