"""
Demo script to create sample documents for testing Phase 2 matching
"""
from data.database import (
    init_db, create_project, create_document, get_documents_with_content
)
from pipeline.document_matching import find_similar


def create_demo_documents():
    """Create sample documents for testing document matching"""

    # Initialize database
    init_db()

    # Create demo project
    try:
        project_id = create_project(
            name="E-Commerce Platform",
            description="Online shopping platform with user management",
            jira_project_key="ECOM",
            tags=["e-commerce", "online", "shopping"]
        )
        print(f"✅ Created project: E-Commerce Platform (ID: {project_id})")
    except Exception as e:
        print(f"⚠️  Project might already exist: {e}")
        project_id = 1  # Assume existing project

    # Sample documents
    documents = [
        {
            "title": "User Authentication System",
            "doc_type": "ba",
            "content": {
                "ekranlar": [
                    {
                        "ekran_adi": "Login Screen",
                        "aciklama": "User login with email and password",
                        "fields": [
                            {"name": "email", "type": "email", "required": True},
                            {"name": "password", "type": "password", "required": True}
                        ]
                    },
                    {
                        "ekran_adi": "Forgot Password",
                        "aciklama": "Password recovery via email",
                        "fields": [
                            {"name": "email", "type": "email", "required": True}
                        ]
                    }
                ],
                "backend_islemler": [
                    {
                        "islem": "User Login",
                        "aciklama": "Authenticate user credentials and create session"
                    }
                ]
            },
            "tags": ["authentication", "security", "login"],
            "jira_keys": ["ECOM-101", "ECOM-102"]
        },
        {
            "title": "User Registration Flow",
            "doc_type": "ba",
            "content": {
                "ekranlar": [
                    {
                        "ekran_adi": "Register Screen",
                        "aciklama": "New user registration form",
                        "fields": [
                            {"name": "name", "type": "text", "required": True},
                            {"name": "email", "type": "email", "required": True},
                            {"name": "password", "type": "password", "required": True},
                            {"name": "confirm_password", "type": "password", "required": True}
                        ]
                    },
                    {
                        "ekran_adi": "Email Verification",
                        "aciklama": "Verify email with OTP code"
                    }
                ],
                "backend_islemler": [
                    {
                        "islem": "Create User Account",
                        "aciklama": "Register new user and send verification email"
                    }
                ]
            },
            "tags": ["registration", "authentication", "user-management"],
            "jira_keys": ["ECOM-103"]
        },
        {
            "title": "Product Catalog Management",
            "doc_type": "ba",
            "content": {
                "ekranlar": [
                    {
                        "ekran_adi": "Product List",
                        "aciklama": "Display all products with filters",
                        "fields": [
                            {"name": "search", "type": "text"},
                            {"name": "category", "type": "dropdown"},
                            {"name": "price_range", "type": "slider"}
                        ]
                    },
                    {
                        "ekran_adi": "Product Detail",
                        "aciklama": "Show product details with images and description"
                    }
                ],
                "backend_islemler": [
                    {
                        "islem": "Get Products",
                        "aciklama": "Fetch products from database with pagination"
                    }
                ]
            },
            "tags": ["product", "catalog", "shopping"],
            "jira_keys": ["ECOM-201", "ECOM-202"]
        },
        {
            "title": "Shopping Cart System",
            "doc_type": "ba",
            "content": {
                "ekranlar": [
                    {
                        "ekran_adi": "Shopping Cart",
                        "aciklama": "View and manage cart items",
                        "fields": [
                            {"name": "quantity", "type": "number"},
                            {"name": "promo_code", "type": "text"}
                        ]
                    },
                    {
                        "ekran_adi": "Checkout",
                        "aciklama": "Complete purchase with payment"
                    }
                ],
                "backend_islemler": [
                    {
                        "islem": "Add to Cart",
                        "aciklama": "Add selected product to user cart"
                    },
                    {
                        "islem": "Process Payment",
                        "aciklama": "Process payment and create order"
                    }
                ]
            },
            "tags": ["cart", "shopping", "payment"],
            "jira_keys": ["ECOM-301"]
        },
        {
            "title": "Order Management Dashboard",
            "doc_type": "ba",
            "content": {
                "ekranlar": [
                    {
                        "ekran_adi": "Order History",
                        "aciklama": "Display user order history with status"
                    },
                    {
                        "ekran_adi": "Order Details",
                        "aciklama": "Show order items and tracking information"
                    }
                ],
                "backend_islemler": [
                    {
                        "islem": "Get Orders",
                        "aciklama": "Fetch user orders from database"
                    },
                    {
                        "islem": "Track Order",
                        "aciklama": "Get order tracking information"
                    }
                ]
            },
            "tags": ["orders", "tracking", "dashboard"],
            "jira_keys": ["ECOM-401"]
        }
    ]

    # Create documents
    created_ids = []
    for doc in documents:
        try:
            doc_id = create_document(
                project_id=project_id,
                doc_type=doc["doc_type"],
                title=doc["title"],
                content_json=doc["content"],
                description=f"Demo document for testing Phase 2 matching",
                tags=doc["tags"],
                jira_keys=doc["jira_keys"],
                created_by="demo-script"
            )
            created_ids.append(doc_id)
            print(f"✅ Created document: {doc['title']} (ID: {doc_id})")
        except Exception as e:
            print(f"❌ Error creating {doc['title']}: {e}")

    return created_ids


def test_matching():
    """Test document matching with demo documents"""
    print("\n" + "="*60)
    print("🔍 Testing Document Matching")
    print("="*60 + "\n")

    # Get all documents with content
    docs = get_documents_with_content(doc_type="ba", limit=10)

    if len(docs) < 2:
        print("⚠️  Not enough documents for testing. Need at least 2 documents.")
        return

    # Test matching for first document
    target_doc = docs[0]
    candidate_docs = docs[1:]

    print(f"Target Document: {target_doc['title']}")
    print(f"Searching among {len(candidate_docs)} candidate documents...\n")

    # Find similar
    from pipeline.document_matching import find_similar
    similar_docs = find_similar(target_doc, candidate_docs, top_n=3)

    if similar_docs:
        print(f"Found {len(similar_docs)} similar documents:\n")
        for i, (doc, score, breakdown) in enumerate(similar_docs, 1):
            print(f"{i}. {doc['title']}")
            print(f"   Overall Score: {score:.1%}")
            print(f"   - Content (TF-IDF): {breakdown['tfidf_score']:.1%}")
            print(f"   - Metadata: {breakdown['metadata_score']:.1%}")
            print()
    else:
        print("❌ No similar documents found")


if __name__ == "__main__":
    print("🚀 Creating Demo Documents for Phase 2\n")

    # Create demo documents
    doc_ids = create_demo_documents()

    if doc_ids:
        print(f"\n✅ Successfully created {len(doc_ids)} demo documents!")
        print("\nNow you can:")
        print("1. Run: streamlit run app.py")
        print("2. Go to Document Library")
        print("3. Click 'Find Similar' on any document")
        print("\nOr test matching from command line:")
        print("  python demo_documents.py test\n")

        # Test matching if requested
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == "test":
            test_matching()
