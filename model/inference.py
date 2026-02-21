import pickle
import torch
import numpy as np
import matplotlib.pyplot as plt
from model import FlexibleNN as neuralnet
import argparse
from pathlib import Path

class InferenceAnalyzer:
    """Analyze model predictions on test data"""
    
    def __init__(self, model_path, topology, device='cpu'):
        """
        Initialize the analyzer with a trained model
        
        Args:
            model_path: Path to saved model (.pth file)
            topology: Model architecture (e.g., [32, 64, 32, 1])
            device: 'cpu' or 'cuda'
        """
        self.device = device
        self.model = neuralnet(topology)
        checkpoint = torch.load(model_path, map_location=device)

        # Check if it's a checkpoint dict or direct state_dict
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            self.model.load_state_dict(checkpoint['model_state_dict'])
        else:
            self.model.load_state_dict(checkpoint)
        self.model.to(device)
        self.model.eval()
        
        print(f"Loaded model from: {model_path}")
        print(f"Model architecture: {topology}")
        print(f"Using device: {device}")
    
    def load_test_data(self, data_path):
        """Load test data from pickle file"""
        with open(data_path, 'rb') as f:
            test_data = pickle.load(f)
        
        boards = test_data['boards']
        labels = test_data['normalized_labels']
        
        print(f"\nLoaded {len(boards)} test samples")
        print(f"Board shape: {boards.shape}")
        print(f"Labels shape: {labels.shape}")
        print(f"Label range: [{labels.min():.3f}, {labels.max():.3f}]")
        
        return boards, labels
    
    def predict(self, boards):
        """Make predictions on boards"""
        # Flatten boards from (N, 4, 8) to (N, 32)
        boards_flat = torch.FloatTensor(boards.reshape(boards.shape[0], -1)).to(self.device)
        
        with torch.no_grad():
            predictions = self.model(boards_flat)
        
        return predictions.cpu().numpy().flatten()
    
    def calculate_metrics(self, actual, predicted):
        """Calculate performance metrics"""
        mse = np.mean((actual - predicted) ** 2)
        mae = np.mean(np.abs(actual - predicted))
        rmse = np.sqrt(mse)
        
        # R-squared (coefficient of determination)
        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)
        r2 = 1 - (ss_res / ss_tot)
        
        # Pearson correlation
        correlation = np.corrcoef(actual, predicted)[0, 1]
        
        return {
            'mse': mse,
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'correlation': correlation
        }
    
    def plot_predictions_vs_actual(self, actual, predicted, save_path=None):
        """Plot predicted vs actual values"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Scatter plot
        ax1.scatter(actual, predicted, alpha=0.3, s=10)
        
        # Perfect prediction line
        min_val = min(actual.min(), predicted.min())
        max_val = max(actual.max(), predicted.max())
        ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
        
        ax1.set_xlabel('Actual Values', fontsize=12)
        ax1.set_ylabel('Predicted Values', fontsize=12)
        ax1.set_title('Predicted vs Actual', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal', adjustable='box')
        
        # Error distribution
        errors = predicted - actual
        ax2.hist(errors, bins=50, edgecolor='black', alpha=0.7)
        ax2.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Zero Error')
        ax2.axvline(x=errors.mean(), color='green', linestyle='--', linewidth=2, 
                   label=f'Mean Error: {errors.mean():.6f}')
        ax2.set_xlabel('Prediction Error', fontsize=12)
        ax2.set_ylabel('Frequency', fontsize=12)
        ax2.set_title('Error Distribution', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved plot to: {save_path}")
        
        return fig
    
    def plot_error_analysis(self, actual, predicted, save_path=None):
        """Detailed error analysis plots"""
        errors = predicted - actual
        abs_errors = np.abs(errors)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Absolute error vs actual value
        ax1 = axes[0, 0]
        ax1.scatter(actual, abs_errors, alpha=0.3, s=10)
        ax1.set_xlabel('Actual Values', fontsize=11)
        ax1.set_ylabel('Absolute Error', fontsize=11)
        ax1.set_title('Absolute Error vs Actual Value', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=abs_errors.mean(), color='red', linestyle='--', 
                   label=f'Mean Abs Error: {abs_errors.mean():.6f}')
        ax1.legend()
        
        # 2. Error vs predicted value
        ax2 = axes[0, 1]
        ax2.scatter(predicted, errors, alpha=0.3, s=10)
        ax2.axhline(y=0, color='red', linestyle='--', linewidth=2)
        ax2.set_xlabel('Predicted Values', fontsize=11)
        ax2.set_ylabel('Error (Predicted - Actual)', fontsize=11)
        ax2.set_title('Error vs Predicted Value', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # 3. Percentile analysis
        ax3 = axes[1, 0]
        percentiles = np.arange(0, 101, 5)
        error_percentiles = np.percentile(abs_errors, percentiles)
        ax3.plot(percentiles, error_percentiles, linewidth=2, marker='o')
        ax3.set_xlabel('Percentile', fontsize=11)
        ax3.set_ylabel('Absolute Error', fontsize=11)
        ax3.set_title('Error Percentiles', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.axhline(y=abs_errors.mean(), color='red', linestyle='--', alpha=0.5)
        
        # 4. Q-Q plot for normality
        ax4 = axes[1, 1]
        from scipy import stats
        stats.probplot(errors, dist="norm", plot=ax4)
        ax4.set_title('Q-Q Plot (Error Normality)', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved error analysis to: {save_path}")
        
        return fig
    
    def plot_sample_predictions(self, boards, actual, predicted, n_samples=10, save_path=None):
        """Show sample boards with their actual and predicted values"""
        n_samples = min(n_samples, len(boards))
        indices = np.random.choice(len(boards), n_samples, replace=False)
        
        fig, axes = plt.subplots(2, 5, figsize=(15, 6))
        axes = axes.flatten()
        
        for i, idx in enumerate(indices):
            ax = axes[i]
            board = boards[idx]
            
            # Display the board
            ax.imshow(board, cmap='RdYlGn', vmin=-1, vmax=1, aspect='auto')
            ax.set_title(f'Actual: {actual[idx]:.4f}\nPred: {predicted[idx]:.4f}\n'
                        f'Error: {predicted[idx]-actual[idx]:.4f}',
                        fontsize=9)
            ax.axis('off')
        
        plt.suptitle('Sample Boards with Predictions', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved sample predictions to: {save_path}")
        
        return fig
    
    def print_metrics(self, metrics):
        """Print performance metrics"""
        print("\n" + "="*60)
        print("MODEL PERFORMANCE METRICS")
        print("="*60)
        print(f"Mean Squared Error (MSE):        {metrics['mse']:.8f}")
        print(f"Root Mean Squared Error (RMSE):  {metrics['rmse']:.8f}")
        print(f"Mean Absolute Error (MAE):       {metrics['mae']:.8f}")
        print(f"R² Score:                        {metrics['r2']:.6f}")
        print(f"Pearson Correlation:             {metrics['correlation']:.6f}")
        print("="*60 + "\n")
    
    def analyze(self, test_data_path, output_dir='inference_plots'):
        """Complete analysis pipeline"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Load test data
        boards, actual = self.load_test_data(test_data_path)
        
        # Make predictions
        print("\nGenerating predictions...")
        predicted = self.predict(boards)
        
        # Calculate metrics
        metrics = self.calculate_metrics(actual, predicted)
        self.print_metrics(metrics)
        
        # Generate plots
        print("Generating visualizations...")
        
        self.plot_predictions_vs_actual(
            actual, predicted, 
            save_path=f'{output_dir}/predictions_vs_actual.png'
        )
        
        self.plot_error_analysis(
            actual, predicted,
            save_path=f'{output_dir}/error_analysis.png'
        )
        
        self.plot_sample_predictions(
            boards, actual, predicted,
            save_path=f'{output_dir}/sample_predictions.png'
        )
        
        # Save metrics to file
        import json
        metrics_path = f'{output_dir}/metrics.json'
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"Saved metrics to: {metrics_path}")
        
        print(f"\nAll plots saved to: {output_dir}/")
        
        return metrics, actual, predicted

def main():
    parser = argparse.ArgumentParser(description='Analyze neural network predictions on test data')
    parser.add_argument('--test-data', type=str, default='inference_test_data.pkl',
                       help='Path to test data pickle file')
    parser.add_argument('--model', type=str, default='best_model.pth',
                       help='Path to trained model')
    parser.add_argument('--topology', type=int, nargs='+', default=[32, 64, 32, 1],
                       help='Model topology (e.g., 32 64 32 1)')
    parser.add_argument('--output-dir', type=str, default='inference_plots',
                       help='Directory to save plots')
    parser.add_argument('--no-show', action='store_true',
                       help='Don\'t display plots, only save them')
    parser.add_argument('--device', type=str, default='cpu',
                       choices=['cpu', 'cuda'],
                       help='Device to run inference on')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = InferenceAnalyzer(
        model_path=args.model,
        topology=args.topology,
        device=args.device
    )
    
    # Run analysis
    metrics, actual, predicted = analyzer.analyze(
        test_data_path=args.test_data,
        output_dir=args.output_dir
    )
    
    # Show plots if requested
    if not args.no_show:
        print("\nDisplaying plots... (close windows to exit)")
        plt.show()

if __name__ == '__main__':
    main()