export PYTHONPATH=`pwd`/actions
export ENVFILE=.env # choose .env based on environment variable ie. local / development / testing / production
for entry in `ls experiments`; do
    logfile=${entry/json/log}    
    chaos --log-file logs/$logfile run experiments/$entry --journal-path journal/$entry
done