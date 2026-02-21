import matplotlib.pyplot as plt
import pandas as pd
import json
import glob
import os
import argparse
from pathlib import Path

class TrainingVisualizer:
    """Visualize training metrics from log files"""
    
    def __init__(self, log_dir='logs'):
        self.log_dir = log_dir
        
    def load_latest_logs(self):
        """Load the most recent training logs"""
        csv_files = glob.glob(os.path.join(self.log_dir, 'training_log_*.csv'))
        json_files = glob.glob(os.path.join(self.log_dir, 'training_summary_*.json'))
        
        if not csv_files:
            raise FileNotFoundError(f"No training logs found in {self.log_dir}")
        
        # Get the most recent files
        latest_csv = max(csv_files, key=os.path.getctime)
        latest_json = max(json_files, key=os.path.getctime) if json_files else None
        
        print(f"Loading logs from: {latest_csv}")
        
        # Load CSV
        df = pd.read_csv(latest_csv)
        
        # Load JSON summary if available
        summary = None
        if latest_json:
            with open(latest_json, 'r') as f:
                summary = json.load(f)
        
        return df, summary
    
    def load_specific_log(self, log_file):
        """Load a specific log file"""
        if not os.path.exists(log_file):
            raise FileNotFoundError(f"Log file not found: {log_file}")
        
        print(f"Loading logs from: {log_file}")
        df = pd.read_csv(log_file)
        
        # Try to load corresponding JSON
        json_file = log_file.replace('training_log_', 'training_summary_').replace('.csv', '.json')
        summary = None
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                summary = json.load(f)
        
        return df, summary
    
    def plot_loss_curves(self, df, summary=None, save_path=None):
        """Plot training and validation loss curves"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot losses
        ax.plot(df['epoch'], df['train_loss'], label='Training Loss', linewidth=2, marker='o', markersize=3)
        
        if 'val_loss' in df.columns and df['val_loss'].notna().any():
            ax.plot(df['epoch'], df['val_loss'], label='Validation Loss', linewidth=2, marker='s', markersize=3)
            
            # Mark best validation loss
            if summary and 'best_val_loss' in summary:
                best_epoch = df.loc[df['val_loss'] == df['val_loss'].min(), 'epoch'].values[0]
                ax.axvline(x=best_epoch, color='green', linestyle='--', alpha=0.5, 
                          label=f'Best Val Loss (epoch {best_epoch})')
        
        ax.set_xlabel('Epoch', fontsize=12)
        ax.set_ylabel('Loss (MSE)', fontsize=12)
        ax.set_title('Training and Validation Loss Over Time', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Add summary info if available
        if summary:
            config_text = f"Topology: {summary['config']['topology']}\n"
            config_text += f"LR: {summary['config']['learning_rate']}, Batch: {summary['config']['batch_size']}"
            ax.text(0.02, 0.98, config_text, transform=ax.transAxes, 
                   fontsize=9, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved loss curve to: {save_path}")
        
        return fig
    
    def plot_learning_rate(self, df, save_path=None):
        """Plot learning rate schedule"""
        if 'learning_rate' not in df.columns:
            print("No learning rate data found in logs")
            return None
        
        fig, ax = plt.subplots(figsize=(12, 4))
        
        ax.plot(df['epoch'], df['learning_rate'], linewidth=2, color='purple')
        ax.set_xlabel('Epoch', fontsize=12)
        ax.set_ylabel('Learning Rate', fontsize=12)
        ax.set_title('Learning Rate Schedule', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved learning rate plot to: {save_path}")
        
        return fig
    
    def plot_loss_comparison(self, df, save_path=None):
        """Plot training vs validation loss comparison"""
        if 'val_loss' not in df.columns or not df['val_loss'].notna().any():
            print("No validation loss data found")
            return None
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Loss curves
        ax1.plot(df['epoch'], df['train_loss'], label='Train', linewidth=2)
        ax1.plot(df['epoch'], df['val_loss'], label='Validation', linewidth=2)
        ax1.set_xlabel('Epoch', fontsize=12)
        ax1.set_ylabel('Loss', fontsize=12)
        ax1.set_title('Loss Curves', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Overfitting detection: val_loss - train_loss
        gap = df['val_loss'] - df['train_loss']
        ax2.plot(df['epoch'], gap, linewidth=2, color='red')
        ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax2.fill_between(df['epoch'], 0, gap, where=(gap > 0), alpha=0.3, color='red', label='Overfitting')
        ax2.fill_between(df['epoch'], 0, gap, where=(gap <= 0), alpha=0.3, color='green', label='Underfitting')
        ax2.set_xlabel('Epoch', fontsize=12)
        ax2.set_ylabel('Val Loss - Train Loss', fontsize=12)
        ax2.set_title('Overfitting/Underfitting Gap', fontsize=12, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved comparison plot to: {save_path}")
        
        return fig
    
    def plot_all(self, df, summary=None, output_dir='plots'):
        """Generate and save all plots"""
        os.makedirs(output_dir, exist_ok=True)
        
        print("\nGenerating plots...")
        
        # Loss curves
        self.plot_loss_curves(df, summary, 
                             save_path=os.path.join(output_dir, 'loss_curves.png'))
        
        # Learning rate
        self.plot_learning_rate(df, 
                               save_path=os.path.join(output_dir, 'learning_rate.png'))
        
        # Comparison
        self.plot_loss_comparison(df, 
                                 save_path=os.path.join(output_dir, 'loss_comparison.png'))
        
        print(f"\nAll plots saved to: {output_dir}/")
    
    def print_summary(self, summary):
        """Print training summary statistics"""
        if not summary:
            print("No summary data available")
            return
        
        print("\n" + "="*60)
        print("TRAINING SUMMARY")
        print("="*60)
        
        print(f"\nConfiguration:")
        for key, value in summary['config'].items():
            print(f"  {key}: {value}")
        
        print(f"\nTraining Duration: {summary['training_duration_seconds']:.2f} seconds "
              f"({summary['training_duration_seconds']/60:.2f} minutes)")
        print(f"Start Time: {summary['start_time']}")
        print(f"End Time: {summary['end_time']}")
        
        print(f"\nFinal Metrics:")
        print(f"  Best Validation Loss: {summary['best_val_loss']:.6f}")
        print(f"  Final Train Loss: {summary['final_train_loss']:.6f}")
        if summary['final_val_loss']:
            print(f"  Final Validation Loss: {summary['final_val_loss']:.6f}")
        
        print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Visualize neural network training logs')
    parser.add_argument('--log-dir', type=str, default='logs', 
                       help='Directory containing log files')
    parser.add_argument('--log-file', type=str, default=None,
                       help='Specific log file to visualize')
    parser.add_argument('--output-dir', type=str, default='plots',
                       help='Directory to save plots')
    parser.add_argument('--no-show', action='store_true',
                       help='Don\'t display plots, only save them')
    
    args = parser.parse_args()
    
    visualizer = TrainingVisualizer(args.log_dir)
    
    try:
        # Load logs
        if args.log_file:
            df, summary = visualizer.load_specific_log(args.log_file)
        else:
            df, summary = visualizer.load_latest_logs()
        
        # Print summary
        visualizer.print_summary(summary)
        
        # Generate plots
        visualizer.plot_all(df, summary, args.output_dir)
        
        # Show plots if requested
        if not args.no_show:
            print("\nDisplaying plots... (close windows to exit)")
            plt.show()
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())