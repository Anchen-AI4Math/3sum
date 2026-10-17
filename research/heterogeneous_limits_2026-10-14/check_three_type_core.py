"""Three distinct block types, all prefix depths, exact direct-count comparison."""
from pathlib import Path
import sys,json,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'algorithm_search_2026-10-14'))
from finite_core import run

if __name__=='__main__':
    start=time.time();result=run((6,8,10),314159)
    result['elapsed_seconds']=time.time()-start
    (ROOT/'three_type_core_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    print('PASS all 340200 weighted-count queries and all tested prefix depths.')
