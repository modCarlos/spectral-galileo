#!/usr/bin/env python3
"""
Phase 3 Master Orchestrator
Coordinates execution of Grid Search → Walk-Forward → Final Validation
Monitors progress and handles transitions between phases
"""

import sys
import logging
import subprocess
import time
import os
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase3_orchestration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Phase3Orchestrator:
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {}
        self.base_dir = Path('/Users/carlosfuentes/GitHub/spectral-galileo')
        self.venv_python = str(self.base_dir / 'venv' / 'bin' / 'python')
        
    def run_script(self, script_name: str, description: str) -> bool:
        """Run a Phase 3 script and monitor execution"""
        
        print("\n" + "="*80)
        print(f"🚀 PHASE 3: {description}")
        print("="*80)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Script: {script_name}")
        print("="*80)
        
        script_path = self.base_dir / script_name
        log_file = self.base_dir / 'backtest_results' / f'{script_name.replace(".py", "")}_execution.log'
        
        try:
            cmd = [self.venv_python, str(script_path)]
            
            with open(log_file, 'w') as f:
                process = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    cwd=str(self.base_dir)
                )
            
            # Monitor process
            start = datetime.now()
            while process.poll() is None:
                elapsed = (datetime.now() - start).total_seconds() / 60
                print(f"⏳ {description} running... ({elapsed:.1f} minutes elapsed)")
                time.sleep(30)  # Check every 30 seconds
            
            elapsed = (datetime.now() - start).total_seconds() / 60
            
            if process.returncode == 0:
                print(f"✅ {description} completed successfully! ({elapsed:.1f} minutes)")
                logger.info(f"✅ {script_name} completed successfully")
                self.results[script_name] = {
                    'status': 'COMPLETED',
                    'duration_minutes': elapsed,
                    'exit_code': 0
                }
                return True
            else:
                print(f"❌ {description} failed with exit code {process.returncode}")
                logger.error(f"❌ {script_name} failed with exit code {process.returncode}")
                self.results[script_name] = {
                    'status': 'FAILED',
                    'duration_minutes': elapsed,
                    'exit_code': process.returncode
                }
                return False
                
        except Exception as e:
            print(f"❌ Error executing {script_name}: {str(e)}")
            logger.error(f"Error: {str(e)}", exc_info=True)
            self.results[script_name] = {
                'status': 'ERROR',
                'error': str(e)
            }
            return False
    
    def run_phase3(self):
        """Execute all Phase 3 steps in sequence"""
        
        print("\n" + "╔" + "="*78 + "╗")
        print("║" + " "*78 + "║")
        print("║" + "PHASE 3: COMPLETE INTEGRATION EXECUTION".center(78) + "║")
        print("║" + " "*78 + "║")
        print("║" + f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".ljust(77) + "║")
        print("║" + " "*78 + "║")
        print("╚" + "="*78 + "╝")
        
        steps = [
            ('phase3_grid_search_all.py', 'STEP 1: Grid Search Optimization (4-6 hours)'),
            ('phase3_walk_forward.py', 'STEP 2: Walk-Forward Validation (1-2 hours)'),
            ('phase3_final_validation.py', 'STEP 3: Final 8-Ticker Validation (1-2 hours)'),
        ]
        
        completed = 0
        failed = 0
        
        for script, description in steps:
            print(f"\n\n")
            success = self.run_script(script, description)
            
            if success:
                completed += 1
                # Brief pause between scripts
                if script != steps[-1][0]:
                    print(f"\n⏸️  Brief pause before next phase (30 seconds)...")
                    time.sleep(30)
            else:
                failed += 1
                print(f"\n⚠️  Step failed. Continuing with next phase...")
                # Don't stop, continue to next phase
        
        # Summary
        self.print_summary(completed, failed)
    
    def print_summary(self, completed: int, failed: int):
        """Print execution summary"""
        
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        
        print("\n" + "╔" + "="*78 + "╗")
        print("║" + " "*78 + "║")
        print("║" + "PHASE 3 ORCHESTRATION SUMMARY".center(78) + "║")
        print("║" + " "*78 + "║")
        print(f"║ Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}".ljust(77) + "║")
        print(f"║ End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".ljust(77) + "║")
        print(f"║ Total Duration: {elapsed:.1f} minutes".ljust(77) + "║")
        print("║" + " "*78 + "║")
        print(f"║ Steps Completed: {completed}".ljust(77) + "║")
        print(f"║ Steps Failed: {failed}".ljust(77) + "║")
        print("║" + " "*78 + "║")
        print("║ Details:".ljust(77) + "║")
        
        for script, result in self.results.items():
            status = result.get('status', 'UNKNOWN')
            duration = result.get('duration_minutes', 'N/A')
            duration_str = f"{duration:.1f}m" if isinstance(duration, float) else duration
            line = f"║   {script}: {status} ({duration_str})".ljust(77) + "║"
            print(line)
        
        print("║" + " "*78 + "║")
        
        if failed == 0:
            print("║ ✅ ALL PHASES COMPLETE - Phase 3 Ready for Review!".ljust(77) + "║")
        else:
            print(f"║ ⚠️  {failed} phase(s) had issues - check logs for details".ljust(77) + "║")
        
        print("║" + " "*78 + "║")
        print("╚" + "="*78 + "╝")
        
        logger.info(f"Phase 3 Orchestration Complete: {completed} succeeded, {failed} failed")

def main():
    try:
        orchestrator = Phase3Orchestrator()
        orchestrator.run_phase3()
        return 0
    except KeyboardInterrupt:
        print("\n\n❌ Phase 3 orchestration interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Phase 3 orchestration failed: {str(e)}")
        logging.error("Orchestration failed", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
