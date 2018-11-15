#!/bin/sh

#  Uninstall.command
#  QuoteFix
#
#  Created by Jeevanandam M. on 10/9/13.
#  Modified by Robert Klep to work with QuoteFix on 15-11-2018
#

mh_plugin=${HOME}/Library/Mail/Bundles/QuoteFix.mailbundle

echo "\n\nUninstalling QuoteFix plugin"
echo "==================================="
if [ -s ${mh_plugin} ]; then
	confirm="input"
	until [[ ${confirm} =~ (y|Y) || ${confirm} =~ (N) ]]
	do
		echo "\nAre you sure want to uninstall? [y/N]"
		read confirm
	done

	case ${confirm} in
		y|Y)
			echo "Proceeding Uninstall of 'QuoteFix' plugin...";
			rm -rf ${mh_plugin};
			echo "\n====================================================="
			echo "  Plugin uninstallation completed, restart Mail.app  "
			echo "====================================================="
			;;
		N)
			echo "Aborting operation as per user choice... see ya..." ;
			exit 0
			;;
	esac
else
	echo "\nQuoteFix plugin is not installed."
fi
