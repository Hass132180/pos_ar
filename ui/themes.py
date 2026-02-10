"""
الثيمات والألوان
"""
import customtkinter as ctk


class AppTheme:
    """إدارة ثيمات التطبيق"""
    
    # الألوان - Light Theme
    COLORS = {
        "primary": "#1976d2",
        "primary_hover": "#1565c0",
        "secondary": "#f5f5f5",
        "accent": "#2196f3",
        "success": "#43a047",
        "success_hover": "#388e3c",
        "warning": "#ffa000",
        "warning_hover": "#ff8f00",
        "danger": "#e53935",
        "danger_hover": "#b71c1c",
        "bg_dark": "#ffffff",
        "bg_light": "#f5f5f5",
        "surface": "#fafafa",
        "text": "#222222",
        "text_secondary": "#757575",
        "border": "#e0e0e0"
    }
    
    @staticmethod
    def setup():
        """إعداد الثيم العام"""
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
    
    @staticmethod
    def get_button_colors(type="primary"):
        """الحصول على ألوان الأزرار"""
        colors = {
            "primary": (AppTheme.COLORS["primary"], AppTheme.COLORS["primary_hover"]),
            "success": (AppTheme.COLORS["success"], AppTheme.COLORS["success_hover"]),
            "warning": (AppTheme.COLORS["warning"], AppTheme.COLORS["warning_hover"]),
            "danger": (AppTheme.COLORS["danger"], AppTheme.COLORS["danger_hover"]),
        }
        return colors.get(type, colors["primary"])
