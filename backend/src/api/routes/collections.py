"""API routes for Netflix-style collection rows.

Endpoints:
    GET /api/v1/collections  - home screen themed rows
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, get_content_router
from src.api.response import success_envelope
from src.auth.jwt_handler import verify_token
from src.database.crud.preferences import get_preferences
from src.database.crud.rating import get_ratings_by_user
from src.database.crud.user import get_by_id
from src.database.models.user import User
from src.services.collection_service import CollectionService
from src.services.content_router import ContentRouter
from src.services.content_normalizer import (
    SOURCE_GOOGLE_BOOKS,
    SOURCE_COMIC_VINE,
    SOURCE_INTERNET_ARCHIVE,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["collections"])

_bearer = HTTPBearer(auto_error=False)

_CATALOG_SEED: list[dict[str, Any]] = [
    # ── Sci-Fi ──────────────────────────────────────────────────────────────
    {
        "id": "seed-1", "title": "Dune",
        "description": "A science fiction epic set on a desert planet about politics, religion and survival.",
        "genres": ["sci-fi", "adventure", "political"], "mood": "epic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Dune Frank Herbert", "published_date": "1965",
    },
    {
        "id": "seed-2", "title": "Neuromancer",
        "description": "Cyberpunk noir set in a dark dystopian future with hackers and AI.",
        "genres": ["sci-fi", "cyberpunk", "dark"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Neuromancer William Gibson", "published_date": "1984",
    },
    {
        "id": "seed-3", "title": "Foundation",
        "description": "The fall of a galactic empire and the plan to preserve knowledge.",
        "genres": ["sci-fi", "political", "epic"], "mood": "epic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Foundation Isaac Asimov", "published_date": "1951",
    },
    {
        "id": "seed-4", "title": "The Left Hand of Darkness",
        "description": "An envoy visits a planet where inhabitants have no fixed gender.",
        "genres": ["sci-fi", "literary", "philosophical"], "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Left Hand of Darkness Ursula Le Guin", "published_date": "1969",
    },
    {
        "id": "seed-5", "title": "Hyperion",
        "description": "Seven pilgrims travel to meet the terrifying Shrike on a distant world.",
        "genres": ["sci-fi", "horror", "epic"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Hyperion Dan Simmons", "published_date": "1989",
    },
    {
        "id": "seed-14", "title": "The Hitchhiker's Guide to the Galaxy",
        "description": "A man is whisked off Earth moments before its demolition for a hyperspace bypass.",
        "genres": ["sci-fi", "comedy", "absurdist"], "mood": "funny",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Hitchhiker's Guide to the Galaxy Douglas Adams", "published_date": "1979",
    },
    {
        "id": "seed-20", "title": "Ender's Game",
        "description": "A child prodigy is trained in a space battle school to fight an alien war.",
        "genres": ["sci-fi", "adventure", "military"], "mood": "adventurous",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Ender's Game Orson Scott Card", "published_date": "1985",
    },
    {
        "id": "seed-21", "title": "The Martian",
        "description": "An astronaut stranded on Mars must use science and wit to survive alone.",
        "genres": ["sci-fi", "survival", "comedy"], "mood": "funny",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Martian Andy Weir", "published_date": "2011",
    },
    {
        "id": "seed-22", "title": "Annihilation",
        "description": "A team of scientists enters a mysterious forbidden zone where reality breaks down.",
        "genres": ["sci-fi", "horror", "mystery"], "mood": "mysterious",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Annihilation Jeff VanderMeer", "published_date": "2014",
    },
    {
        "id": "seed-23", "title": "Flowers for Algernon",
        "description": "A man with low intelligence undergoes an experiment that transforms his mind.",
        "genres": ["sci-fi", "literary", "emotional"], "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Flowers for Algernon Daniel Keyes", "published_date": "1966",
    },
    {
        "id": "seed-24", "title": "Brave New World",
        "description": "A dystopian society engineered for happiness at the cost of freedom.",
        "genres": ["sci-fi", "dystopia", "philosophical"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Brave New World Aldous Huxley", "published_date": "1932",
    },
    {
        "id": "seed-25", "title": "1984",
        "description": "A man lives under the iron grip of a totalitarian surveillance state.",
        "genres": ["sci-fi", "dystopia", "political"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "1984 George Orwell", "published_date": "1949",
    },
    {
        "id": "seed-26", "title": "The War of the Worlds",
        "description": "Martians invade Earth and humanity scrambles to survive.",
        "genres": ["sci-fi", "adventure", "horror"], "mood": "adventurous",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The War of the Worlds H G Wells", "published_date": "1898",
    },
    {
        "id": "seed-27", "title": "Solaris",
        "description": "Scientists studying a mysterious ocean planet find it reflects their deepest fears.",
        "genres": ["sci-fi", "philosophical", "literary"], "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Solaris Stanislaw Lem", "published_date": "1961",
    },
    {
        "id": "seed-28", "title": "Snow Crash",
        "description": "A hacker-pizza-delivery-man battles a dangerous new drug in a near-future America.",
        "genres": ["sci-fi", "cyberpunk", "action"], "mood": "adventurous",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Snow Crash Neal Stephenson", "published_date": "1992",
    },
    {
        "id": "seed-29", "title": "The Time Machine",
        "description": "A Victorian inventor travels far into the future and finds a strange divided humanity.",
        "genres": ["sci-fi", "adventure", "philosophical"], "mood": "adventurous",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Time Machine H G Wells", "published_date": "1895",
    },
    {
        "id": "seed-200", "title": "Childhood's End",
        "description": "Alien overlords usher in a golden age for humanity but at a hidden cost.",
        "genres": ["sci-fi", "philosophical", "epic"], "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Childhood's End Arthur C Clarke", "published_date": "1953",
    },
    {
        "id": "seed-201", "title": "Rendezvous with Rama",
        "description": "Astronauts explore a vast alien spacecraft drifting through the solar system.",
        "genres": ["sci-fi", "adventure", "mystery"], "mood": "adventurous",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Rendezvous with Rama Arthur C Clarke", "published_date": "1973",
    },
    {
        "id": "seed-202", "title": "The Dispossessed",
        "description": "A physicist travels between two contrasting worlds to unite their societies.",
        "genres": ["sci-fi", "political", "philosophical"], "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Dispossessed Ursula Le Guin", "published_date": "1974",
    },
    {
        "id": "seed-203", "title": "Dark Matter",
        "description": "A physicist is kidnapped and wakes up in a life that isn't his own.",
        "genres": ["sci-fi", "thriller", "mystery"], "mood": "mysterious",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Dark Matter Blake Crouch", "published_date": "2016",
    },
    {
        "id": "seed-204", "title": "Project Hail Mary",
        "description": "A lone astronaut must save Earth but first has to remember who he is.",
        "genres": ["sci-fi", "adventure", "survival"], "mood": "adventurous",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Project Hail Mary Andy Weir", "published_date": "2021",
    },
    {
        "id": "seed-205", "title": "The Three-Body Problem",
        "description": "A secret military project sends signals into space with catastrophic consequences.",
        "genres": ["sci-fi", "political", "epic"], "mood": "epic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Three-Body Problem Liu Cixin", "published_date": "2008",
    },
    {
        "id": "seed-206", "title": "Blindsight",
        "description": "A crew of posthumans investigates a first contact event at the edge of the solar system.",
        "genres": ["sci-fi", "horror", "philosophical"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Blindsight Peter Watts", "published_date": "2006",
    },
    {
        "id": "seed-207", "title": "Old Man's War",
        "description": "Elderly people are given young bodies to fight in an interstellar war.",
        "genres": ["sci-fi", "military", "adventure"], "mood": "adventurous",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Old Man's War John Scalzi", "published_date": "2005",
    },
    # ── Fantasy ─────────────────────────────────────────────────────────────
    {
        "id": "seed-9", "title": "The Name of the Wind",
        "description": "A legendary wizard recounts his extraordinary life story from a quiet inn.",
        "genres": ["fantasy", "adventure", "epic"], "mood": "epic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Name of the Wind Patrick Rothfuss", "published_date": "2007",
    },
    {
        "id": "seed-30", "title": "The Way of Kings",
        "description": "An epic fantasy of war, ancient magic, and the destiny of a broken world.",
        "genres": ["fantasy", "adventure", "epic"], "mood": "epic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Way of Kings Brandon Sanderson", "published_date": "2010",
    },
    {
        "id": "seed-31", "title": "A Wizard of Earthsea",
        "description": "A young wizard discovers his true name and the shadow he unleashed on the world.",
        "genres": ["fantasy", "adventure", "coming-of-age"], "mood": "adventurous",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "A Wizard of Earthsea Ursula Le Guin", "published_date": "1968",
    },
    {
        "id": "seed-32", "title": "The Lies of Locke Lamora",
        "description": "A master thief and con artist runs elaborate schemes in a fantasy city-state.",
        "genres": ["fantasy", "crime", "adventure"], "mood": "adventurous",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Lies of Locke Lamora Scott Lynch", "published_date": "2006",
    },
    {
        "id": "seed-33", "title": "American Gods",
        "description": "Old gods brought to America by immigrants clash with new gods of technology.",
        "genres": ["fantasy", "mythology", "dark"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "American Gods Neil Gaiman", "published_date": "2001",
    },
    {
        "id": "seed-34", "title": "Good Omens",
        "description": "An angel and a demon who have grown fond of Earth conspire to prevent the apocalypse.",
        "genres": ["fantasy", "comedy", "adventure"], "mood": "funny",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Good Omens Terry Pratchett Neil Gaiman", "published_date": "1990",
    },
    {
        "id": "seed-300", "title": "The Hobbit",
        "description": "A homebody hobbit is swept into an epic quest to reclaim a dragon-guarded treasure.",
        "genres": ["fantasy", "adventure", "classic"], "mood": "adventurous",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Hobbit J R R Tolkien", "published_date": "1937",
    },
    {
        "id": "seed-301", "title": "A Game of Thrones",
        "description": "Noble families war for control of the Iron Throne while an ancient evil awakens.",
        "genres": ["fantasy", "political", "dark"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "A Game of Thrones George R R Martin", "published_date": "1996",
    },
    {
        "id": "seed-302", "title": "The Blade Itself",
        "description": "A barbarian, a crippled torturer, and a fading hero are drawn into a vast conspiracy.",
        "genres": ["fantasy", "dark", "adventure"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Blade Itself Joe Abercrombie", "published_date": "2006",
    },
    {
        "id": "seed-303", "title": "Mistborn",
        "description": "A young street thief discovers she has rare powers and joins a heist to overthrow a god-emperor.",
        "genres": ["fantasy", "adventure", "epic"], "mood": "adventurous",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Mistborn Brandon Sanderson", "published_date": "2006",
    },
    {
        "id": "seed-304", "title": "The Colour of Magic",
        "description": "A failed wizard and a naive tourist stumble through a flat world full of absurd magic.",
        "genres": ["fantasy", "comedy", "adventure"], "mood": "funny",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Colour of Magic Terry Pratchett", "published_date": "1983",
    },
    {
        "id": "seed-305", "title": "Jonathan Strange and Mr Norrell",
        "description": "Two magicians attempt to restore English magic during the Napoleonic Wars.",
        "genres": ["fantasy", "historical fiction", "literary"], "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Jonathan Strange and Mr Norrell Susanna Clarke", "published_date": "2004",
    },
    {
        "id": "seed-306", "title": "The Night Circus",
        "description": "Two young magicians are pitted against each other inside a mysterious black and white circus.",
        "genres": ["fantasy", "romance", "magical realism"], "mood": "romantic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Night Circus Erin Morgenstern", "published_date": "2011",
    },
    {
        "id": "seed-307", "title": "Piranesi",
        "description": "A man lives in a labyrinthine house filled with statues and tides, losing his memory.",
        "genres": ["fantasy", "mystery", "literary"], "mood": "mysterious",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Piranesi Susanna Clarke", "published_date": "2020",
    },
    {
        "id": "seed-308", "title": "His Dark Materials",
        "description": "A girl with a truth-telling compass crosses parallel worlds to save humanity.",
        "genres": ["fantasy", "adventure", "philosophical"], "mood": "adventurous",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "His Dark Materials Philip Pullman", "published_date": "1995",
    },
    {
        "id": "seed-309", "title": "The Priory of the Orange Tree",
        "description": "A queendom without an heir, a dragon threat, and three women at the center of it all.",
        "genres": ["fantasy", "epic", "adventure"], "mood": "epic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Priory of the Orange Tree Samantha Shannon", "published_date": "2019",
    },
    # ── Literary / Magical Realism ───────────────────────────────────────────
    {
        "id": "seed-10", "title": "Kafka on the Shore",
        "description": "A surreal journey of a runaway boy and an old man who can talk to cats.",
        "genres": ["literary", "magical realism", "philosophical"], "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Kafka on the Shore Haruki Murakami", "published_date": "2002",
    },
    {
        "id": "seed-11", "title": "The Road",
        "description": "A father and son walk through a burned America trying to stay alive and human.",
        "genres": ["literary", "post-apocalyptic", "dark"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Road Cormac McCarthy", "published_date": "2006",
    },
    {
        "id": "seed-15", "title": "Beloved",
        "description": "A former enslaved woman is haunted by the ghost of her dead daughter.",
        "genres": ["literary", "historical fiction", "dark"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Beloved Toni Morrison", "published_date": "1987",
    },
    {
        "id": "seed-40", "title": "Never Let Me Go",
        "description": "Students at a quiet English boarding school face an unthinkable predetermined fate.",
        "genres": ["literary", "sci-fi", "emotional"], "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Never Let Me Go Kazuo Ishiguro", "published_date": "2005",
    },
    {
        "id": "seed-41", "title": "Crime and Punishment",
        "description": "A destitute student murders a pawnbroker and is consumed by guilt and paranoia.",
        "genres": ["literary", "crime", "philosophical"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Crime and Punishment Dostoevsky", "published_date": "1866",
    },
    {
        "id": "seed-42", "title": "One Hundred Years of Solitude",
        "description": "Seven generations of the Buendía family in the mythical town of Macondo.",
        "genres": ["literary", "magical realism", "epic"], "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "One Hundred Years of Solitude Gabriel Garcia Marquez", "published_date": "1967",
    },
    {
        "id": "seed-43", "title": "The Great Gatsby",
        "description": "The mysterious millionaire Jay Gatsby chases his lost love in Jazz Age New York.",
        "genres": ["literary", "romance", "classic"], "mood": "romantic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Great Gatsby F Scott Fitzgerald", "published_date": "1925",
    },
    {
        "id": "seed-400", "title": "Norwegian Wood",
        "description": "A young man in Tokyo mourns the death of his best friend and falls in love.",
        "genres": ["literary", "romance", "coming-of-age"], "mood": "romantic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Norwegian Wood Haruki Murakami", "published_date": "1987",
    },
    {
        "id": "seed-401", "title": "The Remains of the Day",
        "description": "An English butler reflects on decades of service and a life of missed chances.",
        "genres": ["literary", "historical fiction", "emotional"], "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Remains of the Day Kazuo Ishiguro", "published_date": "1989",
    },
    {
        "id": "seed-402", "title": "Middlemarch",
        "description": "Interlocking lives in a provincial English town reveal the cost of ambition and love.",
        "genres": ["literary", "romance", "classic"], "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Middlemarch George Eliot", "published_date": "1871",
    },
    {
        "id": "seed-403", "title": "To Kill a Mockingbird",
        "description": "A lawyer defends a Black man in the American South while his children watch.",
        "genres": ["literary", "historical fiction", "inspiring"], "mood": "inspiring",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "To Kill a Mockingbird Harper Lee", "published_date": "1960",
    },
    {
        "id": "seed-404", "title": "The Catcher in the Rye",
        "description": "A disillusioned teenager wanders New York after being expelled from school.",
        "genres": ["literary", "coming-of-age", "classic"], "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Catcher in the Rye J D Salinger", "published_date": "1951",
    },
    {
        "id": "seed-405", "title": "Lolita",
        "description": "A middle-aged professor becomes obsessed with a twelve-year-old girl.",
        "genres": ["literary", "dark", "controversial"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Lolita Vladimir Nabokov", "published_date": "1955",
    },
    {
        "id": "seed-406", "title": "Things Fall Apart",
        "description": "A proud Nigerian warrior watches his traditional world collapse under colonialism.",
        "genres": ["literary", "historical fiction", "dark"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Things Fall Apart Chinua Achebe", "published_date": "1958",
    },
    {
        "id": "seed-407", "title": "The Alchemist",
        "description": "A shepherd boy travels from Spain to Egypt in search of a worldly treasure.",
        "genres": ["literary", "philosophical", "inspiring"], "mood": "inspiring",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Alchemist Paulo Coelho", "published_date": "1988",
    },
    {
        "id": "seed-408", "title": "Siddhartha",
        "description": "A young Indian man seeks enlightenment through teachers, love, and river life.",
        "genres": ["literary", "philosophical", "spiritual"], "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Siddhartha Hermann Hesse", "published_date": "1922",
    },
    # ── Mystery / Thriller ───────────────────────────────────────────────────
    {
        "id": "seed-50", "title": "The Girl with the Dragon Tattoo",
        "description": "A disgraced journalist and a hacker investigate a wealthy family's dark secrets.",
        "genres": ["thriller", "mystery", "crime"], "mood": "mysterious",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Girl with the Dragon Tattoo Stieg Larsson", "published_date": "2005",
    },
    {
        "id": "seed-51", "title": "Gone Girl",
        "description": "A woman vanishes on her wedding anniversary and her husband becomes the suspect.",
        "genres": ["thriller", "mystery", "dark"], "mood": "mysterious",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Gone Girl Gillian Flynn", "published_date": "2012",
    },
    {
        "id": "seed-52", "title": "And Then There Were None",
        "description": "Ten strangers lured to an island are murdered one by one by an unseen killer.",
        "genres": ["mystery", "thriller", "classic"], "mood": "mysterious",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "And Then There Were None Agatha Christie", "published_date": "1939",
    },
    {
        "id": "seed-53", "title": "In the Woods",
        "description": "A Dublin detective investigates a murder site where children vanished decades ago.",
        "genres": ["mystery", "thriller", "literary"], "mood": "mysterious",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "In the Woods Tana French", "published_date": "2007",
    },
    {
        "id": "seed-500", "title": "Big Little Lies",
        "description": "Three women in a wealthy seaside town share a secret that ends in murder.",
        "genres": ["thriller", "mystery", "drama"], "mood": "mysterious",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Big Little Lies Liane Moriarty", "published_date": "2014",
    },
    {
        "id": "seed-501", "title": "The Silent Patient",
        "description": "A famous painter shoots her husband then never speaks again.",
        "genres": ["thriller", "mystery", "psychological"], "mood": "mysterious",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Silent Patient Alex Michaelides", "published_date": "2019",
    },
    {
        "id": "seed-502", "title": "Sharp Objects",
        "description": "A journalist returns to her hometown to investigate two girls' murders.",
        "genres": ["thriller", "mystery", "dark"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Sharp Objects Gillian Flynn", "published_date": "2006",
    },
    {
        "id": "seed-503", "title": "The Da Vinci Code",
        "description": "A symbologist races to solve a murder inside the Louvre involving a secret society.",
        "genres": ["thriller", "mystery", "adventure"], "mood": "adventurous",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Da Vinci Code Dan Brown", "published_date": "2003",
    },
    {
        "id": "seed-504", "title": "Rebecca",
        "description": "A young bride is haunted by the memory of her husband's first wife.",
        "genres": ["mystery", "gothic", "romance"], "mood": "mysterious",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Rebecca Daphne du Maurier", "published_date": "1938",
    },
    {
        "id": "seed-505", "title": "The Woman in White",
        "description": "A drawing teacher uncovers a sinister conspiracy involving a mysterious woman.",
        "genres": ["mystery", "thriller", "classic"], "mood": "mysterious",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Woman in White Wilkie Collins", "published_date": "1859",
    },
    {
        "id": "seed-506", "title": "Tinker Tailor Soldier Spy",
        "description": "A retired spy is brought back to find a Soviet mole at the top of British intelligence.",
        "genres": ["thriller", "spy", "mystery"], "mood": "mysterious",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Tinker Tailor Soldier Spy John le Carre", "published_date": "1974",
    },
    {
        "id": "seed-507", "title": "The Girl on the Train",
        "description": "A troubled woman becomes obsessed with a couple she watches from her train window.",
        "genres": ["thriller", "mystery", "psychological"], "mood": "mysterious",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Girl on the Train Paula Hawkins", "published_date": "2015",
    },
    # ── Romance ─────────────────────────────────────────────────────────────
    {
        "id": "seed-60", "title": "Jane Eyre",
        "description": "An orphan governess falls for the brooding, secretive Mr Rochester.",
        "genres": ["romance", "gothic", "classic"], "mood": "romantic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Jane Eyre Charlotte Bronte", "published_date": "1847",
    },
    {
        "id": "seed-61", "title": "Outlander",
        "description": "A World War II nurse is swept back to 18th century Scotland and falls for a warrior.",
        "genres": ["romance", "historical fiction", "adventure"], "mood": "romantic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Outlander Diana Gabaldon", "published_date": "1991",
    },
    {
        "id": "seed-62", "title": "The Notebook",
        "description": "A summer romance between two people from different worlds spans decades.",
        "genres": ["romance", "drama"], "mood": "romantic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Notebook Nicholas Sparks", "published_date": "1996",
    },
    {
        "id": "seed-600", "title": "Wuthering Heights",
        "description": "A doomed love between a wild foundling and a headstrong girl tears two families apart.",
        "genres": ["romance", "gothic", "classic"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Wuthering Heights Emily Bronte", "published_date": "1847",
    },
    {
        "id": "seed-601", "title": "Anna Karenina",
        "description": "A Russian aristocrat risks everything for a passionate but destructive love affair.",
        "genres": ["romance", "literary", "classic"], "mood": "romantic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Anna Karenina Leo Tolstoy", "published_date": "1878",
    },
    {
        "id": "seed-602", "title": "Me Before You",
        "description": "A quirky young woman becomes the carer of a paralysed man who changes her life.",
        "genres": ["romance", "drama", "emotional"], "mood": "romantic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Me Before You Jojo Moyes", "published_date": "2012",
    },
    {
        "id": "seed-603", "title": "The Fault in Our Stars",
        "description": "Two teenagers with cancer fall in love at a support group.",
        "genres": ["romance", "coming-of-age", "emotional"], "mood": "romantic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Fault in Our Stars John Green", "published_date": "2012",
    },
    {
        "id": "seed-604", "title": "Atonement",
        "description": "A thirteen-year-old's lie tears apart two lovers and haunts her for the rest of her life.",
        "genres": ["romance", "literary", "historical fiction"], "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Atonement Ian McEwan", "published_date": "2001",
    },
    {
        "id": "seed-605", "title": "The Bronze Horseman",
        "description": "Two young people fall in love in Leningrad during World War II.",
        "genres": ["romance", "historical fiction", "war"], "mood": "romantic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Bronze Horseman Paullina Simons", "published_date": "2000",
    },
    # ── Horror ──────────────────────────────────────────────────────────────
    {
        "id": "seed-80", "title": "It",
        "description": "A shapeshifting evil preys on children in a small Maine town across two timelines.",
        "genres": ["horror", "adventure", "dark"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "It Stephen King", "published_date": "1986",
    },
    {
        "id": "seed-81", "title": "House of Leaves",
        "description": "A family discovers their house is larger on the inside than the outside.",
        "genres": ["horror", "literary", "mystery"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "House of Leaves Mark Z Danielewski", "published_date": "2000",
    },
    {
        "id": "seed-82", "title": "Mexican Gothic",
        "description": "A glamorous socialite investigates a creepy mansion in 1950s rural Mexico.",
        "genres": ["horror", "gothic", "mystery"], "mood": "mysterious",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Mexican Gothic Silvia Moreno-Garcia", "published_date": "2020",
    },
    {
        "id": "seed-700", "title": "The Shining",
        "description": "A writer takes a winter caretaker job at a haunted hotel with his family.",
        "genres": ["horror", "psychological", "dark"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Shining Stephen King", "published_date": "1977",
    },
    {
        "id": "seed-701", "title": "Haunting of Hill House",
        "description": "Four people investigate a notoriously haunted mansion and slowly lose their minds.",
        "genres": ["horror", "gothic", "mystery"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Haunting of Hill House Shirley Jackson", "published_date": "1959",
    },
    {
        "id": "seed-702", "title": "Bird Box",
        "description": "A mother blindfolds her children to survive creatures that drive people mad on sight.",
        "genres": ["horror", "thriller", "survival"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Bird Box Josh Malerman", "published_date": "2014",
    },
    {
        "id": "seed-703", "title": "Plain Bad Heroines",
        "description": "A cursed all-girls school in the early 1900s mirrors dark events in the present day.",
        "genres": ["horror", "gothic", "literary"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Plain Bad Heroines Emily M Danforth", "published_date": "2020",
    },
    {
        "id": "seed-704", "title": "The Terror",
        "description": "Two ships searching for the Northwest Passage are stalked by something on the ice.",
        "genres": ["horror", "historical fiction", "adventure"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Terror Dan Simmons", "published_date": "2007",
    },
    # ── Inspiring / Non-fiction ──────────────────────────────────────────────
    {
        "id": "seed-70", "title": "Sapiens",
        "description": "A sweeping history of humankind from the Stone Age to the Silicon Age.",
        "genres": ["non-fiction", "history", "science"], "mood": "educational",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Sapiens Yuval Noah Harari", "published_date": "2011",
    },
    {
        "id": "seed-71", "title": "Educated",
        "description": "A woman raised by survivalists in the mountains escapes to earn a Cambridge PhD.",
        "genres": ["memoir", "non-fiction", "inspiring"], "mood": "inspiring",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Educated Tara Westover", "published_date": "2018",
    },
    {
        "id": "seed-72", "title": "The Immortal Life of Henrietta Lacks",
        "description": "A Black woman's cancer cells were taken without consent and changed medicine forever.",
        "genres": ["non-fiction", "science", "biography"], "mood": "inspiring",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Immortal Life of Henrietta Lacks Rebecca Skloot", "published_date": "2010",
    },
    {
        "id": "seed-73", "title": "Man's Search for Meaning",
        "description": "A psychiatrist finds purpose inside Nazi concentration camps through logotherapy.",
        "genres": ["memoir", "philosophy", "inspiring"], "mood": "inspiring",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Man's Search for Meaning Viktor Frankl", "published_date": "1946",
    },
    {
        "id": "seed-74", "title": "Atomic Habits",
        "description": "A practical framework for building good habits and breaking bad ones.",
        "genres": ["self-help", "non-fiction", "psychology"], "mood": "inspiring",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Atomic Habits James Clear", "published_date": "2018",
    },
    {
        "id": "seed-800", "title": "The Power of Now",
        "description": "A spiritual guide to living fully in the present moment.",
        "genres": ["self-help", "spirituality", "philosophy"], "mood": "inspiring",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Power of Now Eckhart Tolle", "published_date": "1997",
    },
    {
        "id": "seed-801", "title": "Thinking Fast and Slow",
        "description": "A Nobel laureate explores the two systems that drive how we think and decide.",
        "genres": ["non-fiction", "psychology", "science"], "mood": "educational",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Thinking Fast and Slow Daniel Kahneman", "published_date": "2011",
    },
    {
        "id": "seed-802", "title": "The Body Keeps the Score",
        "description": "How trauma reshapes the brain and body and what can heal it.",
        "genres": ["non-fiction", "psychology", "science"], "mood": "educational",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Body Keeps the Score Bessel van der Kolk", "published_date": "2014",
    },
    {
        "id": "seed-803", "title": "Quiet",
        "description": "The power of introverts in a world that cannot stop talking.",
        "genres": ["non-fiction", "psychology", "self-help"], "mood": "inspiring",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Quiet Susan Cain", "published_date": "2012",
    },
    {
        "id": "seed-804", "title": "The Subtle Art of Not Giving a F*ck",
        "description": "A counterintuitive approach to living a good life by choosing what matters.",
        "genres": ["self-help", "non-fiction", "philosophy"], "mood": "funny",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Subtle Art of Not Giving a Fck Mark Manson", "published_date": "2016",
    },
    {
        "id": "seed-805", "title": "Born a Crime",
        "description": "Trevor Noah grows up mixed-race in apartheid South Africa with dark humour.",
        "genres": ["memoir", "biography", "inspiring"], "mood": "inspiring",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Born a Crime Trevor Noah", "published_date": "2016",
    },
    {
        "id": "seed-806", "title": "The Diary of a Young Girl",
        "description": "Anne Frank's journal written while hiding from the Nazis in Amsterdam.",
        "genres": ["memoir", "biography", "historical"], "mood": "inspiring",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Diary of a Young Girl Anne Frank", "published_date": "1947",
    },
    {
        "id": "seed-807", "title": "Becoming",
        "description": "Michelle Obama's memoir about growing up on the South Side of Chicago.",
        "genres": ["memoir", "biography", "inspiring"], "mood": "inspiring",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Becoming Michelle Obama", "published_date": "2018",
    },
    {
        "id": "seed-808", "title": "The Tipping Point",
        "description": "How little things can make a big difference and ideas spread like epidemics.",
        "genres": ["non-fiction", "psychology", "social science"], "mood": "educational",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Tipping Point Malcolm Gladwell", "published_date": "2000",
    },
    # ── Historical Fiction ───────────────────────────────────────────────────
    {
        "id": "seed-900", "title": "All the Light We Cannot See",
        "description": "A blind French girl and a German soldier's fates intersect in occupied France.",
        "genres": ["historical fiction", "war", "literary"], "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "All the Light We Cannot See Anthony Doerr", "published_date": "2014",
    },
    {
        "id": "seed-901", "title": "The Book Thief",
        "description": "A girl in Nazi Germany steals books and shares them with people in her basement.",
        "genres": ["historical fiction", "war", "inspiring"], "mood": "inspiring",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Book Thief Markus Zusak", "published_date": "2005",
    },
    {
        "id": "seed-902", "title": "Pillars of the Earth",
        "description": "The building of a cathedral in 12th century England weaves together lives and power.",
        "genres": ["historical fiction", "epic", "adventure"], "mood": "epic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Pillars of the Earth Ken Follett", "published_date": "1989",
    },
    {
        "id": "seed-903", "title": "Wolf Hall",
        "description": "Thomas Cromwell rises to power in the court of Henry VIII.",
        "genres": ["historical fiction", "political", "literary"], "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Wolf Hall Hilary Mantel", "published_date": "2009",
    },
    {
        "id": "seed-904", "title": "Lincoln in the Bardo",
        "description": "Abraham Lincoln grieves his dead son while ghosts in a cemetery grapple with death.",
        "genres": ["historical fiction", "literary", "fantasy"], "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Lincoln in the Bardo George Saunders", "published_date": "2017",
    },
    {
        "id": "seed-905", "title": "The Name of the Rose",
        "description": "A monk investigates a series of murders in a 14th century Italian monastery.",
        "genres": ["historical fiction", "mystery", "literary"], "mood": "mysterious",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Name of the Rose Umberto Eco", "published_date": "1980",
    },
    # ── Public domain ────────────────────────────────────────────────────────
    {
        "id": "seed-6", "title": "Pride and Prejudice",
        "description": "Elizabeth Bennet and the proud Mr Darcy navigate love and class in Regency England.",
        "genres": ["romance", "literary", "classic"], "mood": "romantic",
        "source": SOURCE_INTERNET_ARCHIVE,
        "search_query": "Pride and Prejudice Jane Austen",
        "published_date": "1813", "is_public_domain": True,
    },
    {
        "id": "seed-7", "title": "Frankenstein",
        "description": "A scientist creates life from dead matter and must face the consequences.",
        "genres": ["horror", "gothic", "philosophical"], "mood": "dark",
        "source": SOURCE_INTERNET_ARCHIVE,
        "search_query": "Frankenstein Mary Shelley",
        "published_date": "1818", "is_public_domain": True,
    },
    {
        "id": "seed-13", "title": "Moby Dick",
        "description": "Captain Ahab's all-consuming obsession with hunting the white whale.",
        "genres": ["literary", "adventure", "classic"], "mood": "epic",
        "source": SOURCE_INTERNET_ARCHIVE,
        "search_query": "Moby Dick Herman Melville",
        "published_date": "1851", "is_public_domain": True,
    },
    {
        "id": "seed-90", "title": "The Count of Monte Cristo",
        "description": "A man wrongly imprisoned escapes to exact elaborate revenge on his enemies.",
        "genres": ["adventure", "literary", "classic"], "mood": "adventurous",
        "source": SOURCE_INTERNET_ARCHIVE,
        "search_query": "The Count of Monte Cristo Alexandre Dumas",
        "published_date": "1844", "is_public_domain": True,
    },
    {
        "id": "seed-91", "title": "Adventures of Huckleberry Finn",
        "description": "A boy and a runaway slave journey down the Mississippi River to freedom.",
        "genres": ["adventure", "literary", "classic"], "mood": "adventurous",
        "source": SOURCE_INTERNET_ARCHIVE,
        "search_query": "Adventures of Huckleberry Finn Mark Twain",
        "published_date": "1884", "is_public_domain": True,
    },
    {
        "id": "seed-92", "title": "Dracula",
        "description": "A Transylvanian vampire comes to England and a band of heroes must stop him.",
        "genres": ["horror", "gothic", "classic"], "mood": "dark",
        "source": SOURCE_INTERNET_ARCHIVE,
        "search_query": "Dracula Bram Stoker",
        "published_date": "1897", "is_public_domain": True,
    },
    {
        "id": "seed-93", "title": "The Picture of Dorian Gray",
        "description": "A vain young man trades his soul to stay beautiful while his portrait ages.",
        "genres": ["literary", "gothic", "philosophical"], "mood": "dark",
        "source": SOURCE_INTERNET_ARCHIVE,
        "search_query": "The Picture of Dorian Gray Oscar Wilde",
        "published_date": "1890", "is_public_domain": True,
    },
    {
        "id": "seed-94", "title": "War and Peace",
        "description": "Five aristocratic families navigate love and loss during Napoleon's invasion of Russia.",
        "genres": ["literary", "historical fiction", "epic", "classic"], "mood": "epic",
        "source": SOURCE_INTERNET_ARCHIVE,
        "search_query": "War and Peace Leo Tolstoy",
        "published_date": "1869", "is_public_domain": True,
    },
    {
        "id": "seed-95", "title": "The Brothers Karamazov",
        "description": "Three brothers wrestle with faith, doubt, and guilt after their father is murdered.",
        "genres": ["literary", "philosophical", "classic"], "mood": "thoughtful",
        "source": SOURCE_INTERNET_ARCHIVE,
        "search_query": "The Brothers Karamazov Dostoevsky",
        "published_date": "1880", "is_public_domain": True,
    },
    {
        "id": "seed-96", "title": "Don Quixote",
        "description": "A man driven mad by chivalric romances sets out as a knight to right the world's wrongs.",
        "genres": ["literary", "adventure", "comedy", "classic"], "mood": "funny",
        "source": SOURCE_INTERNET_ARCHIVE,
        "search_query": "Don Quixote Miguel de Cervantes",
        "published_date": "1605", "is_public_domain": True,
    },
    {
        "id": "seed-97", "title": "Great Expectations",
        "description": "An orphan boy named Pip grows up dreaming of becoming a gentleman.",
        "genres": ["literary", "coming-of-age", "classic"], "mood": "thoughtful",
        "source": SOURCE_INTERNET_ARCHIVE,
        "search_query": "Great Expectations Charles Dickens",
        "published_date": "1861", "is_public_domain": True,
    },
    {
        "id": "seed-98", "title": "The Odyssey",
        "description": "Odysseus spends ten years trying to return home after the fall of Troy.",
        "genres": ["adventure", "mythology", "classic", "epic"], "mood": "epic",
        "source": SOURCE_INTERNET_ARCHIVE,
        "search_query": "The Odyssey Homer",
        "published_date": "800BC", "is_public_domain": True,
    },
    {
        "id": "seed-99", "title": "Sherlock Holmes",
        "description": "The world's greatest detective solves London's most baffling crimes.",
        "genres": ["mystery", "adventure", "classic"], "mood": "mysterious",
        "source": SOURCE_INTERNET_ARCHIVE,
        "search_query": "Adventures of Sherlock Holmes Arthur Conan Doyle",
        "published_date": "1892", "is_public_domain": True,
    },
    # ── Comics / Graphic Novels ──────────────────────────────────────────────
    {
        "id": "seed-8", "title": "Saga",
        "description": "Two soldiers from opposite sides of a galactic war raise a child on the run.",
        "genres": ["sci-fi", "comics", "adventure"], "mood": "adventurous",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Saga Brian K Vaughan", "published_date": "2012",
    },
    {
        "id": "seed-12", "title": "Maus",
        "description": "Art Spiegelman's father recounts surviving the Holocaust, told with mice and cats.",
        "genres": ["biography", "history", "comics", "dark"], "mood": "dark",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Maus Art Spiegelman", "published_date": "1991",
    },
    {
        "id": "seed-100", "title": "Watchmen",
        "description": "Retired superheroes investigate a murder in a world that outlawed them.",
        "genres": ["comics", "mystery", "dark", "political"], "mood": "dark",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Watchmen Alan Moore", "published_date": "1987",
    },
    {
        "id": "seed-101", "title": "Sandman",
        "description": "The lord of dreams escapes captivity after 70 years and must rebuild his realm.",
        "genres": ["comics", "fantasy", "mythology", "dark"], "mood": "fantastical",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Sandman Neil Gaiman", "published_date": "1989",
    },
    {
        "id": "seed-102", "title": "Persepolis",
        "description": "A young girl comes of age during the Iranian Revolution and its aftermath.",
        "genres": ["comics", "memoir", "biography", "inspiring"], "mood": "inspiring",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Persepolis Marjane Satrapi", "published_date": "2000",
    },
    {
        "id": "seed-103", "title": "Batman Year One",
        "description": "Bruce Wayne and James Gordon both begin their careers in a corrupt Gotham City.",
        "genres": ["comics", "crime", "adventure", "dark"], "mood": "dark",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Batman Year One Frank Miller", "published_date": "1987",
    },
    {
        "id": "seed-104", "title": "V for Vendetta",
        "description": "A masked anarchist fights a fascist government in a dystopian future Britain.",
        "genres": ["comics", "political", "dystopia", "dark"], "mood": "dark",
        "source": SOURCE_COMIC_VINE,
        "search_query": "V for Vendetta Alan Moore", "published_date": "1988",
    },
    {
        "id": "seed-105", "title": "Bone",
        "description": "Three cartoon cousins are lost in a vast valley full of monsters and mysteries.",
        "genres": ["comics", "fantasy", "adventure", "funny"], "mood": "adventurous",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Bone Jeff Smith", "published_date": "1991",
    },
    {
        "id": "seed-106", "title": "Preacher",
        "description": "A Texas preacher with a supernatural power hunts God across America.",
        "genres": ["comics", "adventure", "dark", "funny"], "mood": "adventurous",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Preacher Garth Ennis", "published_date": "1995",
    },
    {
        "id": "seed-107", "title": "Y The Last Man",
        "description": "Every mammal with a Y chromosome dies suddenly except one man and his monkey.",
        "genres": ["comics", "sci-fi", "adventure"], "mood": "adventurous",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Y The Last Man Brian K Vaughan", "published_date": "2002",
    },
    {
        "id": "seed-108", "title": "From Hell",
        "description": "A meticulous retelling of the Jack the Ripper murders in Victorian London.",
        "genres": ["comics", "historical fiction", "mystery", "dark"], "mood": "dark",
        "source": SOURCE_COMIC_VINE,
        "search_query": "From Hell Alan Moore", "published_date": "1989",
    },
    {
        "id": "seed-109", "title": "Fables",
        "description": "Fairy tale characters have been exiled to live secretly in modern New York City.",
        "genres": ["comics", "fantasy", "adventure", "mystery"], "mood": "fantastical",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Fables Bill Willingham", "published_date": "2002",
    },
    {
        "id": "seed-110", "title": "Transmetropolitan",
        "description": "A gonzo journalist exposes corruption in a depraved far-future city.",
        "genres": ["comics", "sci-fi", "political", "funny"], "mood": "funny",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Transmetropolitan Warren Ellis", "published_date": "1997",
    },
    {
        "id": "seed-111", "title": "The Walking Dead",
        "description": "A sheriff's deputy leads a group of survivors through a zombie apocalypse.",
        "genres": ["comics", "horror", "adventure", "dark"], "mood": "dark",
        "source": SOURCE_COMIC_VINE,
        "search_query": "The Walking Dead Robert Kirkman", "published_date": "2003",
    },
    {
        "id": "seed-112", "title": "Invincible",
        "description": "A teenager inherits superpowers from his father but discovers a dark secret.",
        "genres": ["comics", "superhero", "adventure", "dark"], "mood": "adventurous",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Invincible Robert Kirkman", "published_date": "2003",
    },
    {
        "id": "seed-113", "title": "Black Panther",
        "description": "The king of Wakanda fights to protect his nation from threats within and without.",
        "genres": ["comics", "superhero", "political", "adventure"], "mood": "epic",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Black Panther Ta-Nehisi Coates", "published_date": "2016",
    },
    {
        "id": "seed-114", "title": "Ms Marvel",
        "description": "A Pakistani-American Muslim teenager from New Jersey discovers she has superpowers.",
        "genres": ["comics", "superhero", "coming-of-age", "funny"], "mood": "adventurous",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Ms Marvel Kamala Khan", "published_date": "2014",
    },
    {
        "id": "seed-115", "title": "Hawkeye",
        "description": "What does Hawkeye do when he is not being an Avenger? Gets into trouble.",
        "genres": ["comics", "superhero", "funny", "crime"], "mood": "funny",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Hawkeye Matt Fraction", "published_date": "2012",
    },
    {
        "id": "seed-116", "title": "Locke and Key",
        "description": "Three siblings move into their ancestral home and discover magical keys.",
        "genres": ["comics", "horror", "fantasy", "mystery"], "mood": "mysterious",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Locke and Key Joe Hill", "published_date": "2008",
    },
    {
        "id": "seed-117", "title": "East of West",
        "description": "Death rides through an alternate America where the apocalypse is a political conspiracy.",
        "genres": ["comics", "sci-fi", "dark", "political"], "mood": "dark",
        "source": SOURCE_COMIC_VINE,
        "search_query": "East of West Jonathan Hickman", "published_date": "2013",
    },
    {
        "id": "seed-118", "title": "Paper Girls",
        "description": "Four newspaper delivery girls stumble into a time war in 1980s Ohio.",
        "genres": ["comics", "sci-fi", "adventure", "mystery"], "mood": "adventurous",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Paper Girls Brian K Vaughan", "published_date": "2015",
    },
]
_CATALOG_BY_ID: dict[str, dict[str, Any]] = {
    item["id"]: item for item in _CATALOG_SEED
}


def _source_prefix(external_source: str) -> str:
    if external_source == SOURCE_COMIC_VINE:
        return "cv"
    if external_source == SOURCE_INTERNET_ARCHIVE:
        return "ia"
    return "gb"


async def _enrich_item_real(
    seed: dict[str, Any],
    content_router: ContentRouter,
) -> dict[str, Any] | None:
    source = seed.get("source", SOURCE_GOOGLE_BOOKS)
    query = seed.get("search_query") or seed.get("title", "")

    try:
        if source == SOURCE_GOOGLE_BOOKS:
            results = await content_router.search(
                query=query, limit=1, sources=[SOURCE_GOOGLE_BOOKS],
            )
        elif source == SOURCE_COMIC_VINE:
            results = await content_router.search(
                query=query, limit=1, sources=[SOURCE_COMIC_VINE],
            )
        elif source == SOURCE_INTERNET_ARCHIVE:
            results = await content_router.search(
                query=query, limit=1, sources=[SOURCE_INTERNET_ARCHIVE],
            )
        else:
            results = []

        if results:
            item = results[0]
            return {
                "content_id": item["content_id"],
                "title": item["title"],
                "author": item.get("author") or "Unknown",
                "cover_url": item.get("cover_url"),
                "content_type": item.get("content_type", "book"),
                "is_free": item.get("is_free", False),
                "free_url": item.get("free_url"),
                "source": item.get("source", source),
                "description": item.get("description"),
                "genres": item.get("genres") or seed.get("genres", []),
            }

    except Exception:
        logger.warning(
            "Failed to enrich seed item from API",
            extra={"seed_id": seed.get("id"), "source": source, "query": query},
            exc_info=True,
        )

    return None


async def _enrich_row_real(
    row: dict[str, Any],
    content_router: ContentRouter,
) -> dict[str, Any]:
    raw_items = row.get("items", [])
    seeds: list[dict[str, Any]] = []

    for entry in raw_items:
        if isinstance(entry, str):
            seed = _CATALOG_BY_ID.get(entry)
            if seed is not None:
                seeds.append(seed)
        elif isinstance(entry, dict):
            seeds.append(entry)

    tasks = [_enrich_item_real(seed, content_router) for seed in seeds]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    enriched: list[dict[str, Any]] = []
    seen_content_ids: set[str] = set()
    for result in results:
        if isinstance(result, dict):
            cid = result.get("content_id", "")
            if cid and cid not in seen_content_ids:
                seen_content_ids.add(cid)
                enriched.append(result)
        elif isinstance(result, Exception):
            logger.warning(
                "Item enrichment raised exception",
                extra={"error": str(result)},
            )

    return {
        "id": row.get("id", ""),
        "title": row.get("title", ""),
        "mood": row.get("mood", ""),
        "items": enriched,
        "item_count": len(enriched),
    }


async def _get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if credentials is None:
        return None

    user_id_str = verify_token(credentials.credentials, expected_type="access")
    if user_id_str is None:
        return None

    try:
        from uuid import UUID
        user_id = UUID(user_id_str)
    except ValueError:
        return None

    return await get_by_id(db, user_id)


@router.get(
    "/api/v1/collections",
    status_code=status.HTTP_200_OK,
)
async def get_collections(
    request: Request,
    n_collections: int = Query(default=20, ge=1, le=30),
    row_limit: int = Query(default=20, ge=1, le=50),
    current_user: User | None = Depends(_get_optional_user),
    db: AsyncSession = Depends(get_db),
    content_router: ContentRouter = Depends(get_content_router),
) -> dict[str, Any]:
    """Return themed collection rows for the home screen."""
    user_id: str | None = None
    user_ratings: list[dict[str, Any]] = []
    content_preference = "both"

    if current_user is not None:
        user_id = str(current_user.id)

        ratings_result, _ = await get_ratings_by_user(
            db,
            user_id=current_user.id,
            limit=100,
            offset=0,
        )

        for r in ratings_result:
            if r.book is None:
                continue
            prefix = _source_prefix(r.book.external_source)
            content_id = f"{prefix}:{r.book.external_id}"
            user_ratings.append({
                "user_id": str(current_user.id),
                "content_id": content_id,
                "rating": float(r.rating),
                "title": r.book.title,
            })

        prefs = await get_preferences(db, user_id=current_user.id)
        if prefs is not None and hasattr(prefs, "content_type_preference"):
            content_preference = getattr(prefs, "content_type_preference", "both")

    service = CollectionService()
    rows = service.build_home_screen(
        catalog=_CATALOG_SEED,
        user_id=user_id,
        user_ratings=user_ratings,
        content_preference=content_preference,
        n_collections=n_collections,
        row_limit=row_limit,
    )

    enrich_tasks = [_enrich_row_real(row, content_router) for row in rows]
    enriched_rows = await asyncio.gather(*enrich_tasks, return_exceptions=True)

    final_rows: list[dict[str, Any]] = []
    for result in enriched_rows:
        if isinstance(result, dict) and result.get("items"):
            final_rows.append(result)
        elif isinstance(result, Exception):
            logger.warning(
                "Row enrichment raised exception",
                extra={"error": str(result)},
            )

    return success_envelope(
        {
            "rows": final_rows,
            "total": len(final_rows),
            "personalized": user_id is not None and len(user_ratings) > 0,
        }
    )