
# EN1 Studies:

python morePVs.py -p EN1_value_of_pv2 -s siteA_value8 -t False && python morePVs.py -p EN1_value_of_pv2 -s siteB_value8 -t False && python morePVs.py -p EN1_value_of_pv2 -s siteC_value8 -t False &
sleep 120
python morePVs.py -p EN1_value_of_pv2 -s siteD_value8 -t False && python morePVs.py -p EN1_value_of_pv2 -s siteE_value8 -t False && python morePVs.py -p EN1_value_of_pv2 -s siteF_value8 -t False &
sleep 120
python morePVs.py -p EN1_value_of_pv2 -s siteG_value8 -t False && python morePVs.py -p EN1_value_of_pv2 -s siteH_value8 -t False &
sleep 120
python morePVs.py -p EN1_value_of_pv2 -s siteJ_value8 -t False && python morePVs.py -p EN1_value_of_pv2 -s siteI_value8 -t False &
sleep 120
python morePVs.py -p EN1a_pv_bat3 -s siteJ_bat3_3 -t True && python morePVs.py -p EN1a_pv_bat3 -s siteJ_bat3_5 -t True &
sleep 120
python morePVs.py -p EN1a_pv_bat3 -s siteJ_bat3_4 -t True && python morePVs.py -p EN1a_pv_bat3 -s siteJ_bat3_6 -t True &
