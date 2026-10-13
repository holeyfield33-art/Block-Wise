P=/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/venv/bin/python
A=/tmp/claude-0/-home-user/fe51d682-0577-53e5-8f5b-f05cb53542c4/scratchpad/wsmain/r04/app/inventory.py
d=$(mktemp -d); cd $d
r(){ echo "\$ $*"; $P $A "$@"; echo "[rc=$?]"; }
r; r add apple 3; r add pear 10; r low; r low 0; r low x; r low -1; r remove apple 5; r remove kiwi 1
r remove apple 3; r show; r add Bad 1; r add apple 0; r add apple 3.0; r add apple; r foo; r show x; r low 1 2
echo garbage > inventory.json; r show
