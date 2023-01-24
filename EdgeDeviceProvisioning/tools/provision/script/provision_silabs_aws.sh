# !/bin/bash

USAGE="\n
#########################################################################################################\n
COMMANDER_BIN_PATH must point to Simplicity Commander tool binary path and must be exported\n
\n
Usage: ./provision_silabs.sh <arg1> <arg2> <arg3>\n
\t<arg1>: Silabs MCU series (bg21 or bg24)\n
\t<arg2>: Aws Device Profile response (device_profile.json)\n
\t<arg3>: Aws Wireless Device response (wireless_device.json)\n
#########################################################################################################"
MGF_IMG=mfg.s37
NVM3_FILE=mfg.nvm3
INIT_FILE=initfile.s37

if [ $# != 3 ] ; then
  echo ${USAGE}
  exit 1;
fi

series=$1
device_profile=$2
wireless_device=$3

if [ "${series}" != "xg21" ] && [ "${series}" != "xg24" ] ; then
  echo ${USAGE}
  exit 1;
fi

if [[ -z "${COMMANDER_BIN_PATH}" ]]; then
  echo "Set and export COMMANDER_BIN_PATH environment variable"
  exit 1;
else
  echo $("${COMMANDER_BIN_PATH}"/commander --version)
fi

if [[ -z "${device_profile}" ]]; then
  echo "device profile response json is not provided"
  exit 1;
fi

if [[ -z "${wireless_device}" ]]; then
  echo "wireless device response json is not provided"
  exit 1;
fi

echo "Invoking provisioning script"
python3 provision.py aws --device_profile_json ${device_profile} --wireless_device_json ${wireless_device} --output_sl_nvm3 ${NVM3_FILE}

echo "Creating init file for ${series}"
if [ "${series}" == "xg21" ] ; then
  "${COMMANDER_BIN_PATH}"/commander nvm3 initfile --address 0x000F2000 --size 0x6000 --device EFR32MG21A020F1024IM32 --outfile ${INIT_FILE}
else
  "${COMMANDER_BIN_PATH}"/commander nvm3 initfile --address 0x08172000 --size 0x6000 --device EFR32MG24A020F1536GM48 --outfile ${INIT_FILE}
fi

echo "Creating manufacturing image for ${series}"
"${COMMANDER_BIN_PATH}"/commander nvm3 set ${INIT_FILE} --nvm3file ${NVM3_FILE} --outfile ${MGF_IMG} > /dev/null

if [ -f "${MGF_IMG}" ]; then
  echo "Removing intermediary files"
  rm ${NVM3_FILE} ${INIT_FILE}
else
  echo "Manufacturing image can't be created"
  exit 1;
fi

echo "Manufacturing image created - ${MGF_IMG}"
