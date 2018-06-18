loadFile = os.path.join(load_path, load_list[0])
temp_load = pd.read_csv(loadFile,
                        parse_dates=['timestamp'],
                        dayfirst=True)
dict_load_profiles[load_list[0]] = temp_load.set_index('timestamp')
