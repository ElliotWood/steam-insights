"""
Batch processing utilities for LLM enrichment.
Handles job management, progress tracking, and error recovery.
"""

import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging

from src.models.database import (
    Game, Review, GameEnrichment, BatchProcessingJob
)
from src.utils.llm_enrichment import GameEnrichmentExtractor

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Manage batch processing jobs for game enrichment."""
    
    def __init__(
        self,
        db_session: Session,
        extractor: GameEnrichmentExtractor,
        batch_size: int = 100,
        max_errors: int = 10
    ):
        self.db = db_session
        self.extractor = extractor
        self.batch_size = batch_size
        self.max_errors = max_errors
        self._should_pause = False
    
    def create_job(
        self,
        total_items: int,
        config: Optional[Dict[str, Any]] = None
    ) -> BatchProcessingJob:
        """Create a new batch processing job."""
        job = BatchProcessingJob(
            job_type='llm_enrichment',
            total_items=total_items,
            processed_items=0,
            failed_items=0,
            status='pending',
            progress_percentage=0.0,
            config=json.dumps(config or {}),
            results_summary=json.dumps({}),
            error_log=json.dumps([])
        )
        self.db.add(job)
        self.db.commit()
        return job
    
    def get_active_job(self) -> Optional[BatchProcessingJob]:
        """Get the currently active job (running or paused)."""
        return self.db.query(BatchProcessingJob).filter(
            BatchProcessingJob.status.in_(['running', 'paused'])
        ).order_by(desc(BatchProcessingJob.created_at)).first()
    
    def get_latest_job(self) -> Optional[BatchProcessingJob]:
        """Get the most recent job."""
        return self.db.query(BatchProcessingJob).order_by(
            desc(BatchProcessingJob.created_at)
        ).first()
    
    def pause_job(self, job_id: int):
        """Pause a running job."""
        job = self.db.query(BatchProcessingJob).get(job_id)
        if job and job.status == 'running':
            job.status = 'paused'
            job.paused_at = datetime.now(timezone.utc)
            self.db.commit()
            self._should_pause = True
    
    def resume_job(self, job_id: int):
        """Resume a paused job."""
        job = self.db.query(BatchProcessingJob).get(job_id)
        if job and job.status == 'paused':
            job.status = 'running'
            job.paused_at = None
            self.db.commit()
            self._should_pause = False
    
    def cancel_job(self, job_id: int):
        """Cancel a job."""
        job = self.db.query(BatchProcessingJob).get(job_id)
        if job and job.status in ['running', 'paused', 'pending']:
            job.status = 'failed'
            job.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            self._should_pause = True
    
    def get_games_to_process(
        self,
        limit: Optional[int] = None,
        exclude_processed: bool = True
    ) -> List[Game]:
        """Get games that need enrichment."""
        query = self.db.query(Game)
        
        if exclude_processed:
            # Get games without enrichment or with old enrichment
            processed_ids = self.db.query(
                GameEnrichment.steam_appid
            ).filter(
                GameEnrichment.error_message.is_(None)
            ).all()
            processed_ids = [id[0] for id in processed_ids]
            
            if processed_ids:
                query = query.filter(~Game.steam_appid.in_(processed_ids))
        
        # Prioritize games with more data
        query = query.filter(
            Game.description.isnot(None),
            Game.description != ''
        ).order_by(desc(Game.created_at))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def process_single_game(self, game: Game) -> Dict[str, Any]:
        """Process a single game and return enrichment data."""
        try:
            # Prepare game data
            game_data = {
                'id': game.steam_appid,
                'name': game.name,
                'developer': game.developer,
                'description': game.description,
                'short_description': game.short_description
            }
            
            # Extract features
            features = self.extractor.extract_game_features(game_data)
            
            # Get reviews for sentiment analysis
            reviews = self.db.query(Review).filter(
                Review.steam_appid == game.steam_appid
            ).limit(50).all()
            
            reviews_data = [
                {
                    'review_text': r.review_text,
                    'is_positive': r.is_positive
                }
                for r in reviews
            ]
            
            # Analyze sentiment
            sentiment = self.extractor.analyze_sentiment(
                game_data,
                reviews_data
            )
            
            # Combine results
            enrichment_data = {
                **features,
                **sentiment
            }
            
            return enrichment_data
            
        except Exception as e:
            logger.error(f"Error processing game {game.steam_appid}: {e}")
            return {
                'error_message': str(e),
                'confidence_score': 0.0
            }
    
    def save_enrichment(
        self,
        steam_appid: int,
        enrichment_data: Dict[str, Any]
    ):
        """Save or update game enrichment data."""
        existing = self.db.query(GameEnrichment).filter(
            GameEnrichment.steam_appid == steam_appid
        ).first()
        
        if existing:
            # Update existing
            for key, value in enrichment_data.items():
                if key in ['mechanics', 'themes', 'features']:
                    setattr(existing, key, json.dumps(value))
                else:
                    setattr(existing, key, value)
            existing.updated_at = datetime.now(timezone.utc)
            existing.processed_at = datetime.now(timezone.utc)
        else:
            # Create new
            enrichment = GameEnrichment(
                steam_appid=steam_appid,
                mechanics=json.dumps(
                    enrichment_data.get('mechanics', [])
                ),
                themes=json.dumps(enrichment_data.get('themes', [])),
                features=json.dumps(enrichment_data.get('features', [])),
                sentiment_score=enrichment_data.get('sentiment_score'),
                sentiment_summary=enrichment_data.get('sentiment_summary'),
                llm_model=enrichment_data.get('llm_model'),
                prompt_version=enrichment_data.get('prompt_version'),
                confidence_score=enrichment_data.get('confidence_score', 0.0),
                processing_time_seconds=enrichment_data.get(
                    'processing_time_seconds', 0.0
                ),
                error_message=enrichment_data.get('error_message'),
                retry_count=0
            )
            self.db.add(enrichment)
        
        self.db.commit()
    
    def run_batch_job(self, job: BatchProcessingJob):
        """Execute a batch processing job."""
        try:
            # Update job status
            job.status = 'running'
            job.started_at = datetime.now(timezone.utc)
            self.db.commit()
            
            # Get config
            config = json.loads(job.config) if job.config else {}
            batch_size = config.get('batch_size', self.batch_size)
            
            # Get games to process
            games = self.get_games_to_process(
                limit=job.total_items,
                exclude_processed=True
            )
            
            if not games:
                job.status = 'completed'
                job.completed_at = datetime.now(timezone.utc)
                job.progress_percentage = 100.0
                self.db.commit()
                return
            
            # Process games
            error_log = []
            processed = 0
            failed = 0
            
            for i, game in enumerate(games):
                # Check for pause
                if self._should_pause:
                    job.status = 'paused'
                    job.paused_at = datetime.now(timezone.utc)
                    self.db.commit()
                    return
                
                try:
                    # Process game
                    enrichment_data = self.process_single_game(game)
                    self.save_enrichment(game.steam_appid, enrichment_data)
                    
                    if enrichment_data.get('error_message'):
                        failed += 1
                        error_log.append({
                            'game_id': game.steam_appid,
                            'game_name': game.name,
                            'error': enrichment_data['error_message'],
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        })
                    else:
                        processed += 1
                    
                except Exception as e:
                    failed += 1
                    error_log.append({
                        'game_id': game.steam_appid,
                        'game_name': game.name,
                        'error': str(e),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
                    logger.error(f"Failed to process game {game.steam_appid}: {e}")
                
                # Update progress
                total_processed = processed + failed
                job.processed_items = total_processed
                job.failed_items = failed
                job.progress_percentage = (
                    total_processed / len(games)
                ) * 100
                
                # Estimate completion time
                if total_processed > 0:
                    elapsed = (
                        datetime.now(timezone.utc) - job.started_at
                    ).total_seconds()
                    avg_time_per_item = elapsed / total_processed
                    remaining = len(games) - total_processed
                    eta_seconds = remaining * avg_time_per_item
                    job.estimated_completion = (
                        datetime.now(timezone.utc) +
                        timedelta(seconds=eta_seconds)
                    )
                
                # Save progress periodically
                if total_processed % 10 == 0:
                    job.error_log = json.dumps(error_log)
                    self.db.commit()
                
                # Stop if too many errors
                if failed > self.max_errors:
                    job.status = 'failed'
                    job.completed_at = datetime.now(timezone.utc)
                    job.error_log = json.dumps(error_log)
                    self.db.commit()
                    return
            
            # Job completed
            job.status = 'completed'
            job.completed_at = datetime.now(timezone.utc)
            job.progress_percentage = 100.0
            job.error_log = json.dumps(error_log)
            job.results_summary = json.dumps({
                'total_processed': processed,
                'total_failed': failed,
                'success_rate': processed / (processed + failed)
                if (processed + failed) > 0 else 0
            })
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Batch job failed: {e}")
            job.status = 'failed'
            job.completed_at = datetime.now(timezone.utc)
            self.db.commit()
