import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description='Run ZIT parallel simulation')
    parser.add_argument('--mode', choices=['python', 'cython'], required=True,
                        help='Which implementation to run')
    args = parser.parse_args()

    if args.mode == 'python':
        from src.py import main as sim
        sim.run_model()
    elif args.mode == 'cython':
        # Cython modules need to be imported from their directory
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'cy'))
        import main as sim
        sim.run_model()

if __name__ == '__main__':
    main()
