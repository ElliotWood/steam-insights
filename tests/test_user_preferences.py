"""
Tests for user preferences and customization.
"""

import pytest
import os
import json
import tempfile
from pathlib import Path
from src.utils.user_preferences import (
    UserPreferences,
    SavedViewManager,
    BookmarkManager,
    KeyboardShortcutManager,
    ThemeManager,
    RecentSearchManager,
    export_preferences,
    import_preferences
)


@pytest.fixture
def temp_prefs_dir(tmp_path):
    """Create a temporary preferences directory."""
    return tmp_path


@pytest.fixture
def user_prefs(temp_prefs_dir, monkeypatch):
    """Create a UserPreferences instance with temporary directory."""
    # Monkey patch Path.home() to return temp directory
    monkeypatch.setattr(Path, 'home', lambda: temp_prefs_dir)
    return UserPreferences(user_id="test_user")


class TestUserPreferences:
    """Test user preferences."""
    
    def test_create_preferences(self, user_prefs):
        """Test creating preferences."""
        assert user_prefs.user_id == "test_user"
        assert user_prefs.preferences is not None
        assert 'theme' in user_prefs.preferences
    
    def test_get_preference(self, user_prefs):
        """Test getting a preference value."""
        theme = user_prefs.get('theme')
        assert theme == 'dark'
        
        # Non-existent key with default
        value = user_prefs.get('nonexistent', 'default_value')
        assert value == 'default_value'
    
    def test_set_preference(self, user_prefs):
        """Test setting a preference value."""
        user_prefs.set('test_key', 'test_value')
        assert user_prefs.get('test_key') == 'test_value'
    
    def test_reset_preferences(self, user_prefs):
        """Test resetting preferences to defaults."""
        user_prefs.set('custom_key', 'custom_value')
        assert user_prefs.get('custom_key') == 'custom_value'
        
        user_prefs.reset()
        assert user_prefs.get('custom_key') is None
        assert user_prefs.get('theme') == 'dark'  # Default
    
    def test_preferences_persistence(self, temp_prefs_dir, monkeypatch):
        """Test that preferences persist across instances."""
        monkeypatch.setattr(Path, 'home', lambda: temp_prefs_dir)
        
        # Create and set value
        prefs1 = UserPreferences(user_id="persist_test")
        prefs1.set('persist_key', 'persist_value')
        
        # Create new instance
        prefs2 = UserPreferences(user_id="persist_test")
        assert prefs2.get('persist_key') == 'persist_value'


class TestSavedViewManager:
    """Test saved view manager."""
    
    def test_save_view(self, user_prefs):
        """Test saving a view."""
        manager = SavedViewManager(user_prefs)
        
        config = {
            'filters': {'genre': 'Action'},
            'sort': 'name'
        }
        
        success = manager.save_view('My View', 'Test view', config)
        assert success
        
        views = manager.list_views()
        assert len(views) >= 1
        assert views[0]['name'] == 'My View'
    
    def test_load_view(self, user_prefs):
        """Test loading a saved view."""
        manager = SavedViewManager(user_prefs)
        
        config = {'setting': 'value'}
        manager.save_view('Test View', 'Description', config)
        
        loaded = manager.load_view('Test View')
        assert loaded is not None
        assert loaded['config'] == config
    
    def test_update_existing_view(self, user_prefs):
        """Test updating an existing view."""
        manager = SavedViewManager(user_prefs)
        
        # Save initial
        manager.save_view('Update View', 'Initial', {'key': 'value1'})
        
        # Update
        manager.save_view('Update View', 'Updated', {'key': 'value2'})
        
        loaded = manager.load_view('Update View')
        assert loaded['config']['key'] == 'value2'
        assert loaded['description'] == 'Updated'
    
    def test_delete_view(self, user_prefs):
        """Test deleting a saved view."""
        manager = SavedViewManager(user_prefs)
        
        manager.save_view('Delete Me', 'Will be deleted', {})
        assert manager.load_view('Delete Me') is not None
        
        success = manager.delete_view('Delete Me')
        assert success
        assert manager.load_view('Delete Me') is None
    
    def test_list_views(self, user_prefs):
        """Test listing all views."""
        manager = SavedViewManager(user_prefs)
        
        manager.save_view('View 1', 'First', {})
        manager.save_view('View 2', 'Second', {})
        
        views = manager.list_views()
        assert len(views) >= 2


class TestBookmarkManager:
    """Test bookmark manager."""
    
    def test_add_bookmark(self, user_prefs):
        """Test adding a bookmark."""
        manager = BookmarkManager(user_prefs)
        
        success = manager.add_bookmark(730, 'Counter-Strike 2', ['fps', 'multiplayer'])
        assert success
        
        bookmarks = manager.list_bookmarks()
        assert len(bookmarks) >= 1
        assert bookmarks[0]['game_id'] == 730
    
    def test_add_duplicate_bookmark(self, user_prefs):
        """Test adding duplicate bookmark fails."""
        manager = BookmarkManager(user_prefs)
        
        manager.add_bookmark(730, 'CS2')
        success = manager.add_bookmark(730, 'CS2')  # Duplicate
        assert not success
    
    def test_remove_bookmark(self, user_prefs):
        """Test removing a bookmark."""
        manager = BookmarkManager(user_prefs)
        
        manager.add_bookmark(730, 'CS2')
        assert manager.is_bookmarked(730)
        
        success = manager.remove_bookmark(730)
        assert success
        assert not manager.is_bookmarked(730)
    
    def test_is_bookmarked(self, user_prefs):
        """Test checking if game is bookmarked."""
        manager = BookmarkManager(user_prefs)
        
        assert not manager.is_bookmarked(730)
        
        manager.add_bookmark(730, 'CS2')
        assert manager.is_bookmarked(730)
    
    def test_list_bookmarks_with_tag(self, user_prefs):
        """Test listing bookmarks filtered by tag."""
        manager = BookmarkManager(user_prefs)
        
        manager.add_bookmark(730, 'CS2', ['fps'])
        manager.add_bookmark(570, 'Dota 2', ['moba'])
        manager.add_bookmark(440, 'TF2', ['fps'])
        
        fps_bookmarks = manager.list_bookmarks(tag='fps')
        assert len(fps_bookmarks) == 2


class TestKeyboardShortcutManager:
    """Test keyboard shortcut manager."""
    
    def test_get_shortcut(self, user_prefs):
        """Test getting a keyboard shortcut."""
        manager = KeyboardShortcutManager(user_prefs)
        
        shortcut = manager.get_shortcut('search')
        assert shortcut == 'ctrl+k'
    
    def test_set_shortcut(self, user_prefs):
        """Test setting a keyboard shortcut."""
        manager = KeyboardShortcutManager(user_prefs)
        
        success = manager.set_shortcut('custom_action', 'ctrl+shift+x')
        assert success
        
        shortcut = manager.get_shortcut('custom_action')
        assert shortcut == 'ctrl+shift+x'
    
    def test_list_shortcuts(self, user_prefs):
        """Test listing all shortcuts."""
        manager = KeyboardShortcutManager(user_prefs)
        
        shortcuts = manager.list_shortcuts()
        assert isinstance(shortcuts, dict)
        assert 'search' in shortcuts
    
    def test_reset_shortcuts(self, user_prefs):
        """Test resetting shortcuts to defaults."""
        manager = KeyboardShortcutManager(user_prefs)
        
        # Modify a shortcut
        manager.set_shortcut('search', 'alt+f')
        assert manager.get_shortcut('search') == 'alt+f'
        
        # Reset
        manager.reset_shortcuts()
        assert manager.get_shortcut('search') == 'ctrl+k'


class TestThemeManager:
    """Test theme manager."""
    
    def test_get_theme(self, user_prefs):
        """Test getting current theme."""
        manager = ThemeManager(user_prefs)
        
        theme = manager.get_theme()
        assert theme in ['dark', 'light']
    
    def test_set_theme(self, user_prefs):
        """Test setting theme."""
        manager = ThemeManager(user_prefs)
        
        success = manager.set_theme('light')
        assert success
        assert manager.get_theme() == 'light'
    
    def test_set_invalid_theme(self, user_prefs):
        """Test setting invalid theme fails."""
        manager = ThemeManager(user_prefs)
        
        success = manager.set_theme('invalid')
        assert not success
    
    def test_get_accent_color(self, user_prefs):
        """Test getting accent color."""
        manager = ThemeManager(user_prefs)
        
        color = manager.get_accent_color()
        assert color.startswith('#')
        assert len(color) == 7
    
    def test_set_accent_color(self, user_prefs):
        """Test setting accent color."""
        manager = ThemeManager(user_prefs)
        
        success = manager.set_accent_color('#ff0000')
        assert success
        assert manager.get_accent_color() == '#ff0000'
    
    def test_set_invalid_accent_color(self, user_prefs):
        """Test setting invalid accent color fails."""
        manager = ThemeManager(user_prefs)
        
        # Invalid format
        assert not manager.set_accent_color('red')
        assert not manager.set_accent_color('#fff')
    
    def test_get_theme_config(self, user_prefs):
        """Test getting complete theme configuration."""
        manager = ThemeManager(user_prefs)
        
        config = manager.get_theme_config()
        assert 'primary_color' in config
        assert 'background_color' in config
        assert 'text_color' in config


class TestRecentSearchManager:
    """Test recent search manager."""
    
    def test_add_search(self, user_prefs):
        """Test adding a recent search."""
        manager = RecentSearchManager(user_prefs)
        
        manager.add_search('Counter-Strike', 'game')
        
        recent = manager.get_recent_searches()
        assert len(recent) >= 1
        assert recent[0]['query'] == 'Counter-Strike'
    
    def test_get_recent_searches_with_limit(self, user_prefs):
        """Test getting recent searches with limit."""
        manager = RecentSearchManager(user_prefs)
        
        for i in range(15):
            manager.add_search(f'Game {i}', 'game')
        
        recent = manager.get_recent_searches(limit=5)
        assert len(recent) == 5
    
    def test_get_recent_searches_with_type_filter(self, user_prefs):
        """Test filtering recent searches by type."""
        manager = RecentSearchManager(user_prefs)
        
        manager.add_search('Game 1', 'game')
        manager.add_search('Genre 1', 'genre')
        manager.add_search('Game 2', 'game')
        
        game_searches = manager.get_recent_searches(search_type='game')
        assert len(game_searches) == 2
    
    def test_recent_searches_deduplication(self, user_prefs):
        """Test that duplicate searches are deduplicated."""
        manager = RecentSearchManager(user_prefs)
        
        manager.add_search('Duplicate', 'game')
        manager.add_search('Duplicate', 'game')
        
        recent = manager.get_recent_searches()
        # Should only have one entry
        duplicates = [s for s in recent if s['query'] == 'Duplicate']
        assert len(duplicates) == 1
    
    def test_clear_recent_searches(self, user_prefs):
        """Test clearing recent searches."""
        manager = RecentSearchManager(user_prefs)
        
        manager.add_search('Search 1', 'game')
        manager.add_search('Search 2', 'game')
        
        manager.clear_recent_searches()
        
        recent = manager.get_recent_searches()
        assert len(recent) == 0


class TestExportImport:
    """Test export/import preferences."""
    
    def test_export_preferences(self, user_prefs, tmp_path):
        """Test exporting preferences to file."""
        export_file = tmp_path / "export.json"
        
        user_prefs.set('test_key', 'test_value')
        
        success = export_preferences(user_prefs, str(export_file))
        assert success
        assert export_file.exists()
        
        # Verify content
        with open(export_file) as f:
            data = json.load(f)
        assert data['test_key'] == 'test_value'
    
    def test_import_preferences(self, temp_prefs_dir, monkeypatch, tmp_path):
        """Test importing preferences from file."""
        monkeypatch.setattr(Path, 'home', lambda: temp_prefs_dir)
        
        # Create import file
        import_file = tmp_path / "import.json"
        import_data = {
            'theme': 'light',
            'custom_setting': 'imported_value'
        }
        with open(import_file, 'w') as f:
            json.dump(import_data, f)
        
        # Import
        prefs = UserPreferences(user_id="import_test")
        success = import_preferences(prefs, str(import_file))
        assert success
        assert prefs.get('custom_setting') == 'imported_value'
        assert prefs.get('theme') == 'light'
