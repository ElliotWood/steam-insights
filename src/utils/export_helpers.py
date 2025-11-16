"""
Helper functions for exporting data from dashboard.
"""
import pandas as pd
from io import BytesIO
from datetime import datetime


def create_csv_download(df, filename_prefix="steam_insights"):
    """
    Create CSV download button data.
    
    Args:
        df: DataFrame to export
        filename_prefix: Prefix for filename
        
    Returns:
        tuple: (csv_data, filename)
    """
    csv = df.to_csv(index=False)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{filename_prefix}_{timestamp}.csv"
    return csv, filename


def create_excel_download(df, filename_prefix="steam_insights"):
    """
    Create Excel download button data.
    
    Args:
        df: DataFrame to export
        filename_prefix: Prefix for filename
        
    Returns:
        tuple: (excel_data, filename)
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    excel_data = output.getvalue()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{filename_prefix}_{timestamp}.xlsx"
    return excel_data, filename


def create_json_download(df, filename_prefix="steam_insights"):
    """
    Create JSON download button data.
    
    Args:
        df: DataFrame to export
        filename_prefix: Prefix for filename
        
    Returns:
        tuple: (json_data, filename)
    """
    json_str = df.to_json(orient='records', indent=2)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{filename_prefix}_{timestamp}.json"
    return json_str, filename


def create_parquet_download(df, filename_prefix="steam_insights"):
    """
    Create Parquet download button data.
    
    Args:
        df: DataFrame to export
        filename_prefix: Prefix for filename
        
    Returns:
        tuple: (parquet_data, filename)
    """
    output = BytesIO()
    df.to_parquet(output, index=False, engine='pyarrow')
    parquet_data = output.getvalue()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{filename_prefix}_{timestamp}.parquet"
    return parquet_data, filename


def add_export_buttons(df, filename_prefix, label="Export Data"):
    """
    Add export buttons to streamlit interface.
    
    Args:
        df: DataFrame to export
        filename_prefix: Prefix for filename
        label: Label for export section
        
    Returns:
        None (renders buttons in streamlit)
    """
    import streamlit as st
    
    if df is None or len(df) == 0:
        st.info("No data to export")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        csv_data, csv_filename = create_csv_download(df, filename_prefix)
        st.download_button(
            label=f"📥 CSV ({len(df):,} rows)",
            data=csv_data,
            file_name=csv_filename,
            mime="text/csv",
            key=f"csv_{filename_prefix}"
        )
    
    with col2:
        try:
            excel_data, excel_filename = create_excel_download(
                df, filename_prefix
            )
            st.download_button(
                label=f"📥 Excel",
                data=excel_data,
                file_name=excel_filename,
                mime="application/vnd.openxmlformats-officedocument."
                     "spreadsheetml.sheet",
                key=f"excel_{filename_prefix}"
            )
        except ImportError:
            st.caption("Excel export requires openpyxl")
    
    with col3:
        json_data, json_filename = create_json_download(df, filename_prefix)
        st.download_button(
            label=f"📥 JSON",
            data=json_data,
            file_name=json_filename,
            mime="application/json",
            key=f"json_{filename_prefix}"
        )
    
    with col4:
        try:
            parquet_data, parquet_filename = create_parquet_download(
                df, filename_prefix
            )
            st.download_button(
                label=f"📥 Parquet",
                data=parquet_data,
                file_name=parquet_filename,
                mime="application/octet-stream",
                key=f"parquet_{filename_prefix}"
            )
        except ImportError:
            st.caption("Parquet requires pyarrow")
            st.download_button(
                label=f"📥 Download Excel ({len(df):,} rows)",
                data=excel_data,
                file_name=excel_filename,
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                key=f"excel_{filename_prefix}"
            )
        except Exception as e:
            st.info(f"Excel export unavailable: {e}")
