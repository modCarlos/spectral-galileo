#!/usr/bin/env python3
"""
Phase 3 Progress Monitor
Monitorea el progreso del grid search y ejecuta fases siguientes cuando esté listo
"""

import sys
import time
import logging
from datetime import datetime
from pathlib import Path
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Phase3Monitor:
    def __init__(self):
        self.base_dir = Path('/Users/carlosfuentes/GitHub/spectral-galileo')
        self.venv_python = str(self.base_dir / 'venv' / 'bin' / 'python')
        self.log_file = self.base_dir / 'backtest_results' / 'phase3_grid_search_complete.log'
        self.start_time = datetime.now()
        
    def get_log_size(self):
        """Obtiene el tamaño actual del log"""
        if self.log_file.exists():
            return self.log_file.stat().st_size
        return 0
    
    def get_log_lines(self):
        """Obtiene cantidad de líneas en el log"""
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                return len(f.readlines())
        return 0
    
    def is_grid_search_complete(self):
        """Verifica si el grid search ha completado"""
        with open(self.log_file, 'r') as f:
            content = f.read()
            # Busca el resumen final
            return '✅ Category-Based Grid Search completed!' in content or \
                   'GRID SEARCH RESULTS - OPTIMAL PARAMETERS BY CATEGORY' in content
    
    def wait_for_grid_search(self, max_wait_minutes=120):
        """Espera a que grid search complete"""
        print("\n" + "="*80)
        print("PHASE 3: MONITORING GRID SEARCH")
        print("="*80)
        print(f"Start Monitoring: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Log File: {self.log_file}")
        print("="*80)
        
        last_size = 0
        check_count = 0
        
        while True:
            current_size = self.get_log_size()
            current_lines = self.get_log_lines()
            elapsed = (datetime.now() - self.start_time).total_seconds() / 60
            
            print(f"\n[{check_count:03d}] Time: {elapsed:6.1f}m | Log Size: {current_size:10,.0f} bytes | Lines: {current_lines:5,d}")
            
            # Mostrar progreso cada 10 checks
            if check_count % 10 == 0 and check_count > 0:
                rate = (current_size - last_size) / (10 * 30) if check_count > 0 else 0  # bytes/sec
                print(f"      Write Rate: {rate:,.0f} bytes/sec")
            
            # Verificar si completó
            if self.is_grid_search_complete():
                print(f"\n✅ GRID SEARCH COMPLETED!")
                print(f"Total Time: {elapsed:.1f} minutes")
                return True
            
            # Verificar timeout
            if elapsed > max_wait_minutes:
                print(f"\n⚠️  Timeout reached ({max_wait_minutes} minutes)")
                return False
            
            last_size = current_size
            check_count += 1
            
            # Esperar 30 segundos antes del próximo check
            time.sleep(30)
    
    def run_next_phase(self, script_name):
        """Ejecuta la siguiente fase"""
        print(f"\n{'='*80}")
        print(f"🚀 Iniciando: {script_name}")
        print(f"{'='*80}")
        
        script_path = self.base_dir / script_name
        
        try:
            cmd = [self.venv_python, str(script_path)]
            process = subprocess.Popen(
                cmd,
                cwd=str(self.base_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Mostrar output
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                print(line.rstrip())
            
            return_code = process.wait()
            
            if return_code == 0:
                print(f"✅ {script_name} completado exitosamente")
                return True
            else:
                print(f"❌ {script_name} falló con código {return_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

def main():
    monitor = Phase3Monitor()
    
    # Paso 1: Esperar por grid search
    print("\n🔄 Esperando completación de Grid Search...")
    if not monitor.wait_for_grid_search(max_wait_minutes=120):
        print("❌ Grid search timeout o no completado")
        return 1
    
    # Paso 2: Ejecutar walk-forward
    print("\n🔄 Ejecutando Walk-Forward Validation...")
    if not monitor.run_next_phase('phase3_walk_forward.py'):
        print("⚠️  Walk-forward tuvo problemas, continuando...")
    
    # Paso 3: Ejecutar validación final
    print("\n🔄 Ejecutando Final 8-Ticker Validation...")
    if not monitor.run_next_phase('phase3_final_validation.py'):
        print("❌ Final validation falló")
        return 1
    
    print("\n" + "="*80)
    print("✅ PHASE 3 COMPLETE!")
    print("="*80)
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Monitor interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        logging.error("Monitor failed", exc_info=True)
        sys.exit(1)
