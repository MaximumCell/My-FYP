#!/usr/bin/env python3
"""
Manually index the semiconductor material content
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv()

async def index_semiconductor_content():
    """Index the semiconductor content manually"""
    print("🔄 Manually indexing semiconductor content...")
    
    # Sample semiconductor content from the uploaded material
    content = """
Semiconductor Materials

Semiconductor materials are the building blocks of modern electronics—they sit between conductors and insulators in terms of electrical conductivity, and their unique properties allow us to control the flow of electricity in devices like transistors, diodes, solar cells, and integrated circuits.

Definition: Semiconductor materials are substances whose electrical conductivity can be modified by temperature, light, or the addition of impurities (a process called doping).

Types of Semiconductor Materials:

1. Intrinsic Semiconductors
- Pure semiconductor materials without any added impurities
- Examples: Silicon (Si), Germanium (Ge)
- Properties: Moderate conductivity, conductivity increases with temperature

2. Extrinsic Semiconductors
- Doped semiconductors—impurities are added to improve conductivity
- N-Type: Doped with pentavalent atoms (Phosphorus, Arsenic), extra electrons
- P-Type: Doped with trivalent atoms (Boron, Gallium), create holes

3. Compound Semiconductors
- Made from two or more elements (III-V or II-VI groups)
- Examples: Gallium Arsenide (GaAs), Gallium Nitride (GaN), Indium Phosphide (InP)
- Advantages: Higher electron mobility, direct band gaps

4. Alloyed Semiconductors
- Ternary or quaternary compounds
- Examples: AlGaAs, AlGaInP
- Benefits: Tunable band gaps, customizable properties

Properties of Semiconductors:
- Intermediate conductivity between conductors and insulators
- Variable conductivity (increases with temperature/light)
- Negative temperature coefficient
- Two types of charge carriers: electrons and holes
- Moderate band gap (0.6-3 eV)

Band Theory:
- Valence Band: Highest energy band where electrons normally exist
- Conduction Band: Higher energy band for free electron movement
- Band Gap: Energy difference between valence and conduction bands
"""
    
    try:
        # Import content processing functions
        from ai.content_extractor import process_and_index_text
        
        # Material metadata
        material_metadata = {
            'title': 'Semiconductor Materials - Lecture 2',
            'material_type': 'lecture_notes',
            'user_id': 'user_33Bnvi59Kj5HM7gRhX9gUaOmVFw',
            'file_name': 'Lecture__2.docx',
            'material_id': '68dfa26a865cf851758adc77'
        }
        
        print("🚀 Processing and indexing content...")
        result = await process_and_index_text(
            content,
            max_tokens=200,
            overlap=20,
            use_cache=True,
            qdrant_client=None,  # Will create its own
            material_metadata=material_metadata
        )
        
        print(f"✅ Indexing result: {result}")
        
        # Check collection stats after indexing
        from qdrant_client import create_physics_vector_db
        
        qdrant_url = os.getenv('QDRANT_URL', 'https://my-fyp-hcom.onrender.com')
        qdrant_api_key = os.getenv('QDRANT_API_KEY', '')
        
        vector_db = create_physics_vector_db(qdrant_url, qdrant_api_key)
        stats = await vector_db.get_stats()
        print(f"📊 Updated collection stats: {stats}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(index_semiconductor_content())