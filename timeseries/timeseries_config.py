import seaborn as sns


'''
==========
File name of extracted features of article
==========
'''
csv_file = 'output.csv'


'''
==========
Extracted features column name in the csv
==========
'''
features = ['psy_affin_count', 'psy_negemo', 'psy_posemo', 'psy_emotone', 'psy_emotions', 'ri_smog',
            'ri_flesch_kincaid', 'ri_gunning_fog', 's_polarity', 's_subjectivity', 'vr_happax_legomena',
            'vr_happax_dislegomena', 'vr_ttr', 'vr_yules_k']


'''
==========
Time range to display plots between from
==========
'''
start_date = 2015
end_date = 2019


'''
==========
Plot setting
==========
'''
plot_size = (24, 15)
plot_palette = sns.light_palette((0.8, 0, 0, 1), reverse=True)
plot_format = 'svg'
