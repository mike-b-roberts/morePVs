module load python/3.6
cd /home/z5044992/en/morePVs
source /home/z5044992/python_venv/bin/activate


python morePVs.py -p EN1_value_of_pv2 -s siteA_value6 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteB_value6 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteC_value6 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteD_value6 -t True &
sleep 60
python morePVs.py -p EN1_value_of_pv2 -s siteE_value6 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteF_value6 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteG_value6 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteH_value6 -t True &
sleep 60
python morePVs.py -p EN1_value_of_pv2 -s siteI_value6 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteJ_value6 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteA_value5 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteB_value5 -t True &
sleep 60
python morePVs.py -p EN1_value_of_pv2 -s siteC_value5 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteD_value5 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteE_value5 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteF_value5 -t True &
sleep 60
python morePVs.py -p EN1_value_of_pv2 -s siteG_value5 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteH_value5 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteI_value5 -t True && python morePVs.py -p EN1_value_of_pv2 -s siteJ_value5 -t True &

