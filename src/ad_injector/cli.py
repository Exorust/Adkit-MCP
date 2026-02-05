"""CLI commands for managing Qdrant collection."""

import argparse

from .qdrant_service import create_collection, delete_collection, get_collection_info


def main():
    parser = argparse.ArgumentParser(description="Manage Qdrant ad collection")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create collection command
    create_parser = subparsers.add_parser("create", help="Create the Qdrant collection")
    create_parser.add_argument(
        "--dimension",
        type=int,
        default=1536,
        help="Embedding dimension (default: 1536)",
    )

    # Delete collection command
    subparsers.add_parser("delete", help="Delete the Qdrant collection")

    # Info command
    subparsers.add_parser("info", help="Show collection information")

    args = parser.parse_args()

    if args.command == "create":
        create_collection(dimension=args.dimension)
    elif args.command == "delete":
        delete_collection()
    elif args.command == "info":
        info = get_collection_info()
        print(f"Collection: {info['name']}")
        print(f"Status: {info['status']}")
        print(f"Points count: {info['points_count']}")
        print(f"Vectors count: {info['vectors_count']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
