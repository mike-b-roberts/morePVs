cd C:/PYTHONprojects/en

python morePVs.py -p EN1_value_of_pv2 -s siteA_value5 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteB_value5 -t True &
sleep 60
python morePVs.py -p EN1_value_of_pv2 -s siteC_value5 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteD_value5 -t True &
sleep 60
python morePVs.py -p EN1_value_of_pv2 -s siteE_value5 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteF_value5 -t True &
sleep 60
python morePVs.py -p EN1_value_of_pv2 -s siteG_value5 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteH_value5 -t True &
sleep 60
python morePVs.py -p EN1_value_of_pv2 -s siteI_value5 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteJ_value5 -t True &
