
# EN1 Studies:
# and EN1a (aka EN2) bat4
# All revised SS and SC calcs
python morePVs.py -p EN1a_pv_bat4 -s siteJ_bat4_1 -t False && python morePVs.py -p EN1a_pv_bat4 -s siteJ_bat4_2 -t False && python morePVs.py -p EN1a_pv_bat4 -s siteJ_bat4_5 -t False & 
sleep 120
python morePVs.py -p EN1a_pv_bat4 -s siteJ_bat4_3 -t False && python morePVs.py -p EN1a_pv_bat4 -s siteJ_bat4_4 -t False && python morePVs.py -p EN1a_pv_bat4 -s siteJ_bat4_7 -t False &
sleep 120
python morePVs.py -p EN1_value_of_pv2 -s siteA_value9 -t False && python morePVs.py -p EN1_value_of_pv2 -s siteB_value9 -t False && python morePVs.py -p EN1_value_of_pv2 -s siteC_value9 -t False &
sleep 120
python morePVs.py -p EN1_value_of_pv2 -s siteD_value9 -t False && python morePVs.py -p EN1_value_of_pv2 -s siteE_value9 -t False && python morePVs.py -p EN1_value_of_pv2 -s siteF_value9 -t False &
sleep 120
python morePVs.py -p EN1_value_of_pv2 -s siteG_value9 -t False && python morePVs.py -p EN1_value_of_pv2 -s siteH_value9 -t False && python morePVs.py -p EN1a_pv_bat4 -s siteJ_bat4_8 -t False &
sleep 120
python morePVs.py -p EN1_value_of_pv2 -s siteJ_value9 -t False && python morePVs.py -p EN1_value_of_pv2 -s siteI_value9 -t False && python morePVs.py -p EN1a_pv_bat4 -s siteJ_bat4_6 -t False &
sleep 120

