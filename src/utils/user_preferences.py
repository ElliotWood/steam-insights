"""
User preferences and customization for Steam Insights.

This module provides saved views, bookmarks, keyboard shortcuts, and theme customization.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class UserPreferences:
    """
    Manage user preferences and customization.
    """
    
    def __init__(self, user_id: str = "default"):
        """
        Initialize user preferences.
        
        Args:
            user_id: Unique user identifier
        """
        self.user_id = user_id
        self.prefs_dir = Path.home() / '.steam_insights'
        self.prefs_file = self.prefs_dir / f'prefs_{user_id}.json'
        
        # Create directory if not exists
        self.prefs_dir.mkdir(exist_ok=True)
        
        # Load preferences
        self.preferences = self._load_preferences()
    
    def _load_preferences(self) -> Dict[str, Any]:
        """
        Load preferences from file.
        
        Returns:
            dict: User preferences
        """
        if self.prefs_file.exists():
            try:
                with open(self.prefs_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading preferences: {e}")
                return self._get_default_preferences()
        return self._get_default_preferences()
    
    def _save_preferences(self):
        """Save preferences to file."""
        try:
            with open(self.prefs_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """
        Get default preferences.
        
        Returns:
            dict: Default preferences
        """
        return {
            'theme': 'dark',
            'accent_color': '#00d4ff',
            'saved_views': [],
            'bookmarks': [],
            'keyboard_shortcuts': {
                'search': 'ctrl+k',
                'refresh': 'f5',
                'export': 'ctrl+e',
                'help': 'f1'
            },
            'dashboard_layout': {
                'sidebar_collapsed': False,
                'chart_height': 400,
                'table_page_size': 20
            },
            'filters': {},
            'recent_searches': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a preference value.
        
        Args:
            key: Preference key
            default: Default value if key not found
            
        Returns:
            Preference value or default
        """
        return self.preferences.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set a preference value.
        
        Args:
            key: Preference key
            value: Preference value
        """
        self.preferences[key] = value
        self.preferences['updated_at'] = datetime.now().isoformat()
        self._save_preferences()
    
    def reset(self):
        """Reset all preferences to defaults."""
        self.preferences = self._get_default_preferences()
        self._save_preferences()


class SavedViewManager:
    """
    Manage saved dashboard views.
    """
    
    def __init__(self, preferences: UserPreferences):
        """
        Initialize saved view manager.
        
        Args:
            preferences: User preferences instance
        """
        self.preferences = preferences
    
    def save_view(self, name: str, description: str, view_config: Dict[str, Any]) -> bool:
        """
        Save a dashboard view.
        
        Args:
            name: View name
            description: View description
            view_config: View configuration (filters, settings, etc.)
            
        Returns:
            bool: Success status
        """
        saved_views = self.preferences.get('saved_views', [])
        
        # Check if view exists
        existing_index = None
        for i, view in enumerate(saved_views):
            if view['name'] == name:
                existing_index = i
                break
        
        view_data = {
            'name': name,
            'description': description,
            'config': view_config,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        if existing_index is not None:
            # Update existing
            view_data['created_at'] = saved_views[existing_index]['created_at']
            saved_views[existing_index] = view_data
        else:
            # Add new
            saved_views.append(view_data)
        
        self.preferences.set('saved_views', saved_views)
        return True
    
    def load_view(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load a saved view.
        
        Args:
            name: View name
            
        Returns:
            dict: View configuration or None
        """
        saved_views = self.preferences.get('saved_views', [])
        
        for view in saved_views:
            if view['name'] == name:
                return view
        
        return None
    
    def list_views(self) -> List[Dict[str, Any]]:
        """
        List all saved views.
        
        Returns:
            list: List of saved views
        """
        return self.preferences.get('saved_views', [])
    
    def delete_view(self, name: str) -> bool:
        """
        Delete a saved view.
        
        Args:
            name: View name
            
        Returns:
            bool: Success status
        """
        saved_views = self.preferences.get('saved_views', [])
        
        for i, view in enumerate(saved_views):
            if view['name'] == name:
                saved_views.pop(i)
                self.preferences.set('saved_views', saved_views)
                return True
        
        return False


class BookmarkManager:
    """
    Manage game bookmarks.
    """
    
    def __init__(self, preferences: UserPreferences):
        """
        Initialize bookmark manager.
        
        Args:
            preferences: User preferences instance
        """
        self.preferences = preferences
    
    def add_bookmark(self, game_id: int, game_name: str, tags: List[str] = None) -> bool:
        """
        Add a game bookmark.
        
        Args:
            game_id: Game ID
            game_name: Game name
            tags: Optional tags
            
        Returns:
            bool: Success status
        """
        bookmarks = self.preferences.get('bookmarks', [])
        
        # Check if already bookmarked
        for bookmark in bookmarks:
            if bookmark['game_id'] == game_id:
                return False  # Already exists
        
        bookmark_data = {
            'game_id': game_id,
            'game_name': game_name,
            'tags': tags or [],
            'added_at': datetime.now().isoformat()
        }
        
        bookmarks.append(bookmark_data)
        self.preferences.set('bookmarks', bookmarks)
        return True
    
    def remove_bookmark(self, game_id: int) -> bool:
        """
        Remove a game bookmark.
        
        Args:
            game_id: Game ID
            
        Returns:
            bool: Success status
        """
        bookmarks = self.preferences.get('bookmarks', [])
        
        for i, bookmark in enumerate(bookmarks):
            if bookmark['game_id'] == game_id:
                bookmarks.pop(i)
                self.preferences.set('bookmarks', bookmarks)
                return True
        
        return False
    
    def is_bookmarked(self, game_id: int) -> bool:
        """
        Check if a game is bookmarked.
        
        Args:
            game_id: Game ID
            
        Returns:
            bool: True if bookmarked
        """
        bookmarks = self.preferences.get('bookmarks', [])
        
        for bookmark in bookmarks:
            if bookmark['game_id'] == game_id:
                return True
        
        return False
    
    def list_bookmarks(self, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all bookmarks, optionally filtered by tag.
        
        Args:
            tag: Optional tag filter
            
        Returns:
            list: List of bookmarks
        """
        bookmarks = self.preferences.get('bookmarks', [])
        
        if tag:
            return [b for b in bookmarks if tag in b.get('tags', [])]
        
        return bookmarks


class KeyboardShortcutManager:
    """
    Manage keyboard shortcuts.
    """
    
    def __init__(self, preferences: UserPreferences):
        """
        Initialize keyboard shortcut manager.
        
        Args:
            preferences: User preferences instance
        """
        self.preferences = preferences
    
    def get_shortcut(self, action: str) -> Optional[str]:
        """
        Get keyboard shortcut for an action.
        
        Args:
            action: Action name
            
        Returns:
            str: Keyboard shortcut or None
        """
        shortcuts = self.preferences.get('keyboard_shortcuts', {})
        return shortcuts.get(action)
    
    def set_shortcut(self, action: str, shortcut: str) -> bool:
        """
        Set keyboard shortcut for an action.
        
        Args:
            action: Action name
            shortcut: Keyboard shortcut (e.g., 'ctrl+k')
            
        Returns:
            bool: Success status
        """
        shortcuts = self.preferences.get('keyboard_shortcuts', {})
        shortcuts[action] = shortcut
        self.preferences.set('keyboard_shortcuts', shortcuts)
        return True
    
    def list_shortcuts(self) -> Dict[str, str]:
        """
        List all keyboard shortcuts.
        
        Returns:
            dict: Mapping of actions to shortcuts
        """
        return self.preferences.get('keyboard_shortcuts', {})
    
    def reset_shortcuts(self):
        """Reset keyboard shortcuts to defaults."""
        default_shortcuts = {
            'search': 'ctrl+k',
            'refresh': 'f5',
            'export': 'ctrl+e',
            'help': 'f1',
            'save': 'ctrl+s',
            'bookmark': 'ctrl+d',
            'next_page': 'ctrl+right',
            'prev_page': 'ctrl+left'
        }
        self.preferences.set('keyboard_shortcuts', default_shortcuts)


class ThemeManager:
    """
    Manage dashboard themes.
    """
    
    def __init__(self, preferences: UserPreferences):
        """
        Initialize theme manager.
        
        Args:
            preferences: User preferences instance
        """
        self.preferences = preferences
    
    def get_theme(self) -> str:
        """
        Get current theme.
        
        Returns:
            str: Theme name ('dark' or 'light')
        """
        return self.preferences.get('theme', 'dark')
    
    def set_theme(self, theme: str) -> bool:
        """
        Set theme.
        
        Args:
            theme: Theme name ('dark' or 'light')
            
        Returns:
            bool: Success status
        """
        if theme not in ['dark', 'light']:
            return False
        
        self.preferences.set('theme', theme)
        return True
    
    def get_accent_color(self) -> str:
        """
        Get accent color.
        
        Returns:
            str: Hex color code
        """
        return self.preferences.get('accent_color', '#00d4ff')
    
    def set_accent_color(self, color: str) -> bool:
        """
        Set accent color.
        
        Args:
            color: Hex color code (e.g., '#00d4ff')
            
        Returns:
            bool: Success status
        """
        # Basic validation
        if not color.startswith('#') or len(color) != 7:
            return False
        
        self.preferences.set('accent_color', color)
        return True
    
    def get_theme_config(self) -> Dict[str, Any]:
        """
        Get complete theme configuration.
        
        Returns:
            dict: Theme configuration
        """
        theme = self.get_theme()
        accent = self.get_accent_color()
        
        if theme == 'dark':
            return {
                'primary_color': accent,
                'background_color': '#0e1117',
                'secondary_background_color': '#1e2128',
                'text_color': '#fafafa',
                'font': 'sans serif'
            }
        else:  # light theme
            return {
                'primary_color': accent,
                'background_color': '#ffffff',
                'secondary_background_color': '#f0f2f6',
                'text_color': '#262730',
                'font': 'sans serif'
            }


class RecentSearchManager:
    """
    Manage recent searches.
    """
    
    def __init__(self, preferences: UserPreferences):
        """
        Initialize recent search manager.
        
        Args:
            preferences: User preferences instance
        """
        self.preferences = preferences
        self.max_recent = 20
    
    def add_search(self, query: str, search_type: str = 'game'):
        """
        Add a recent search.
        
        Args:
            query: Search query
            search_type: Type of search ('game', 'genre', etc.)
        """
        recent = self.preferences.get('recent_searches', [])
        
        # Remove if already exists
        recent = [s for s in recent if s['query'] != query or s['type'] != search_type]
        
        # Add to beginning
        recent.insert(0, {
            'query': query,
            'type': search_type,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only max_recent
        recent = recent[:self.max_recent]
        
        self.preferences.set('recent_searches', recent)
    
    def get_recent_searches(self, search_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent searches.
        
        Args:
            search_type: Optional type filter
            limit: Maximum number of results
            
        Returns:
            list: Recent searches
        """
        recent = self.preferences.get('recent_searches', [])
        
        if search_type:
            recent = [s for s in recent if s['type'] == search_type]
        
        return recent[:limit]
    
    def clear_recent_searches(self):
        """Clear all recent searches."""
        self.preferences.set('recent_searches', [])


def export_preferences(preferences: UserPreferences, filepath: str) -> bool:
    """
    Export preferences to a file.
    
    Args:
        preferences: User preferences instance
        filepath: Export file path
        
    Returns:
        bool: Success status
    """
    try:
        with open(filepath, 'w') as f:
            json.dump(preferences.preferences, f, indent=2)
        return True
    except Exception as e:
        print(f"Export failed: {e}")
        return False


def import_preferences(preferences: UserPreferences, filepath: str) -> bool:
    """
    Import preferences from a file.
    
    Args:
        preferences: User preferences instance
        filepath: Import file path
        
    Returns:
        bool: Success status
    """
    try:
        with open(filepath, 'r') as f:
            imported = json.load(f)
        
        preferences.preferences = imported
        preferences._save_preferences()
        return True
    except Exception as e:
        print(f"Import failed: {e}")
        return False
