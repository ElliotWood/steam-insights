"""
ETL orchestration pipeline for Steam Insights.
Coordinates execution of all data import sources.
"""
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ETLJob:
    """Represents an ETL job."""
    name: str
    script_path: str
    description: str
    enabled: bool = True
    max_runtime_hours: float = 1.0


class ETLPipeline:
    """Orchestrates ETL jobs for data import."""
    
    def __init__(self):
        """Initialize the ETL pipeline."""
        self.jobs: List[ETLJob] = []
        self.results: Dict[str, Dict] = {}
        
    def register_job(self, job: ETLJob):
        """Register an ETL job."""
        self.jobs.append(job)
        logger.info(f"Registered job: {job.name}")
    
    def run_job(self, job: ETLJob) -> Dict:
        """
        Run a single ETL job.
        
        Returns:
            Dict with status, start_time, end_time, duration, error
        """
        import subprocess
        
        result = {
            'name': job.name,
            'status': 'unknown',
            'start_time': None,
            'end_time': None,
            'duration_seconds': 0,
            'error': None
        }
        
        if not job.enabled:
            result['status'] = 'skipped'
            logger.info(f"Skipping disabled job: {job.name}")
            return result
        
        logger.info(f"Starting job: {job.name}")
        logger.info(f"Description: {job.description}")
        
        start_time = datetime.now()
        result['start_time'] = start_time.isoformat()
        
        try:
            # Run the script
            process = subprocess.run(
                ['python', job.script_path],
                capture_output=True,
                text=True,
                timeout=job.max_runtime_hours * 3600,
                check=False
            )
            
            end_time = datetime.now()
            result['end_time'] = end_time.isoformat()
            result['duration_seconds'] = (end_time - start_time).total_seconds()
            
            if process.returncode == 0:
                result['status'] = 'success'
                logger.info(
                    f"Job completed successfully: {job.name} "
                    f"({result['duration_seconds']:.1f}s)"
                )
            else:
                result['status'] = 'failed'
                result['error'] = process.stderr[-500:] if process.stderr else 'Unknown error'
                logger.error(
                    f"Job failed: {job.name}\n"
                    f"Error: {result['error']}"
                )
                
        except subprocess.TimeoutExpired:
            result['status'] = 'timeout'
            result['error'] = f'Exceeded max runtime of {job.max_runtime_hours} hours'
            logger.error(f"Job timed out: {job.name}")
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            logger.error(f"Job error: {job.name} - {e}")
        
        return result
    
    def run_all(self, stop_on_failure: bool = False) -> Dict[str, Dict]:
        """
        Run all registered jobs sequentially.
        
        Args:
            stop_on_failure: If True, stop pipeline on first failure
            
        Returns:
            Dict mapping job names to their results
        """
        logger.info("=" * 60)
        logger.info("ETL Pipeline Starting")
        logger.info(f"Total jobs: {len(self.jobs)}")
        logger.info("=" * 60)
        
        pipeline_start = datetime.now()
        
        for job in self.jobs:
            result = self.run_job(job)
            self.results[job.name] = result
            
            if stop_on_failure and result['status'] == 'failed':
                logger.error(
                    f"Stopping pipeline due to failure: {job.name}"
                )
                break
        
        pipeline_end = datetime.now()
        pipeline_duration = (pipeline_end - pipeline_start).total_seconds()
        
        # Summary
        logger.info("=" * 60)
        logger.info("ETL Pipeline Complete")
        logger.info(f"Total duration: {pipeline_duration:.1f}s")
        self._print_summary()
        logger.info("=" * 60)
        
        return self.results
    
    def _print_summary(self):
        """Print summary of all job results."""
        success_count = sum(
            1 for r in self.results.values() if r['status'] == 'success'
        )
        failed_count = sum(
            1 for r in self.results.values() if r['status'] == 'failed'
        )
        skipped_count = sum(
            1 for r in self.results.values() if r['status'] == 'skipped'
        )
        
        logger.info(f"Jobs completed: {success_count}")
        logger.info(f"Jobs failed: {failed_count}")
        logger.info(f"Jobs skipped: {skipped_count}")
        
        if failed_count > 0:
            logger.info("\nFailed jobs:")
            for name, result in self.results.items():
                if result['status'] == 'failed':
                    logger.info(f"  - {name}: {result.get('error', 'Unknown')}")


def create_default_pipeline() -> ETLPipeline:
    """Create the default ETL pipeline with all sources."""
    pipeline = ETLPipeline()
    
    # Zenodo imports (already complete, disabled by default)
    pipeline.register_job(ETLJob(
        name='Zenodo Release Dates',
        script_path='src/etl/zenodo/import_release_dates.py',
        description='Import release dates from Zenodo dataset',
        enabled=False,  # Already complete
        max_runtime_hours=0.5
    ))
    
    pipeline.register_job(ETLJob(
        name='Zenodo Tag Associations',
        script_path='src/etl/zenodo/import_tag_associations.py',
        description='Import tag associations from Zenodo dataset',
        enabled=False,  # Already complete
        max_runtime_hours=1.0
    ))
    
    pipeline.register_job(ETLJob(
        name='Zenodo Genre Associations',
        script_path='src/etl/zenodo/import_genre_associations.py',
        description='Import genre associations from Zenodo dataset',
        enabled=False,  # Already complete
        max_runtime_hours=1.0
    ))
    
    # SteamSpy import (new, enabled by default)
    pipeline.register_job(ETLJob(
        name='SteamSpy Player Stats',
        script_path='src/etl/steamspy/import_player_stats.py',
        description='Import player statistics from SteamSpy API',
        enabled=True,
        max_runtime_hours=8.0  # Full import ~6 hours
    ))
    
    return pipeline


def main():
    """Main entry point for ETL orchestration."""
    pipeline = create_default_pipeline()
    
    # Run all jobs
    results = pipeline.run_all(stop_on_failure=False)
    
    # Exit with error code if any jobs failed
    failed = any(r['status'] == 'failed' for r in results.values())
    exit(1 if failed else 0)


if __name__ == '__main__':
    main()
