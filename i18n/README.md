## to generate plugin's i18n files

0. generate pro file (\*.pro) from '..\*.py' and '..\*.ui' files :  
$ ./0_generate_pro_file.sh 

1. generate translation files (\*.ts) from '\*.pro' file :  
$ ./1_generate_ts_files.sh 

2. generate compiled translation files ('\*.qm) from translation files ('\*.ts') files :  
$ ./2_generate_qm_files.sh

cf. https://docs.qgis.org/3.10/fr/docs/pyqgis_developer_cookbook/plugins/plugins.html#files-and-directory
