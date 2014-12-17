#!/bin/bash
c()
{
  if [ ! -e "$1" ]
  then
    curl -Lo "$1" "$2"
  fi
}
c "Spectra T-Series Libraries XML Command Reference.pdf" "http://www.spectralogic.com/index.cfm?fuseaction=home.displayFile&DocID=4244"
