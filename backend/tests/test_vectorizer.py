"""Tests for ContentVectorizer — TF-IDF similarity engine."""

import os
import pytest
from src.ml.vectorizer import ContentVectorizer

# Fixtures

SAMPLE_BOOKS = [
    {"id": "book_001", "title": "Harry Potter and the Philosopher's Stone", "authors": ["J.K. Rowling"], "description": "A young wizard discovers he is famous in the magical world and begins his education at Hogwarts School of Witchcraft and Wizardry.", "genres": ["Fantasy", "Young Adult"], "categories": ["Magic", "School", "Adventure"]},
    {"id": "book_002", "title": "Harry Potter and the Chamber of Secrets", "authors": ["J.K. Rowling"], "description": "Harry Potter returns to Hogwarts and discovers a mysterious chamber has been opened releasing a monster that attacks students.", "genres": ["Fantasy", "Young Adult"], "categories": ["Magic", "School", "Mystery"]},
    {"id": "book_003", "title": "The Fellowship of the Ring", "authors": ["J.R.R. Tolkien"], "description": "A hobbit named Frodo inherits a powerful ring and must journey with a fellowship of companions to destroy it in the fires of Mount Doom.", "genres": ["Fantasy", "Epic"], "categories": ["Quest", "Adventure", "Magic"]},
    {"id": "book_004", "title": "The Two Towers", "authors": ["J.R.R. Tolkien"], "description": "The fellowship is broken and Frodo continues toward Mordor with Samwise while Aragorn leads the fight against Saruman's forces.", "genres": ["Fantasy", "Epic"], "categories": ["Quest", "Adventure", "War"]},
    {"id": "book_005", "title": "Dune", "authors": ["Frank Herbert"], "description": "On the desert planet Arrakis a young nobleman named Paul Atreides navigates politics religion and ecology to become a messianic leader.", "genres": ["Science Fiction", "Epic"], "categories": ["Space", "Politics", "Adventure"]},
    {"id": "book_006", "title": "Dune Messiah", "authors": ["Frank Herbert"], "description": "Paul Atreides is now emperor of the known universe but faces conspiracies from multiple factions seeking to destroy his rule on Arrakis.", "genres": ["Science Fiction", "Epic"], "categories": ["Space", "Politics", "Power"]},
    {"id": "book_007", "title": "Foundation", "authors": ["Isaac Asimov"], "description": "A mathematician predicts the fall of galactic civilization and establishes a foundation to preserve human knowledge through the dark ages.", "genres": ["Science Fiction"], "categories": ["Space", "Politics", "History"]},
    {"id": "book_008", "title": "Foundation and Empire", "authors": ["Isaac Asimov"], "description": "The Foundation faces its greatest threat from a mutant called the Mule who cannot be predicted by the mathematical science of psychohistory.", "genres": ["Science Fiction"], "categories": ["Space", "Politics", "War"]},
    {"id": "book_009", "title": "Neuromancer", "authors": ["William Gibson"], "description": "A washed-up computer hacker is hired by a mysterious employer to pull off the ultimate hack in a dystopian cyberpunk future.", "genres": ["Science Fiction", "Cyberpunk"], "categories": ["Technology", "Hacking", "Dystopia"]},
    {"id": "book_010", "title": "Snow Crash", "authors": ["Neal Stephenson"], "description": "In a future America a hacker and pizza delivery driver investigates a virtual reality drug and conspiracy that threatens civilization.", "genres": ["Science Fiction", "Cyberpunk"], "categories": ["Technology", "Hacking", "Virtual Reality"]},
    {"id": "book_011", "title": "The Name of the Wind", "authors": ["Patrick Rothfuss"], "description": "A legendary wizard named Kvothe tells the true story of his life from his childhood in a traveling troupe to his time at a magical university.", "genres": ["Fantasy"], "categories": ["Magic", "Adventure", "Music"]},
    {"id": "book_012", "title": "The Wise Man's Fear", "authors": ["Patrick Rothfuss"], "description": "Kvothe leaves the university to seek his fortune and learns the art of war fighting and the ways of the Adem mercenaries.", "genres": ["Fantasy"], "categories": ["Magic", "Adventure", "War"]},
    {"id": "book_013", "title": "A Game of Thrones", "authors": ["George R.R. Martin"], "description": "Noble families fight for control of the Iron Throne of the Seven Kingdoms while an ancient enemy awakens beyond the northern wall.", "genres": ["Fantasy", "Epic"], "categories": ["Politics", "War", "Dragons"]},
    {"id": "book_014", "title": "A Clash of Kings", "authors": ["George R.R. Martin"], "description": "Five kings wage war across Westeros fighting for the Iron Throne as supernatural threats gather in the frozen north.", "genres": ["Fantasy", "Epic"], "categories": ["Politics", "War", "Dragons"]},
    {"id": "book_015", "title": "The Hitchhiker's Guide to the Galaxy", "authors": ["Douglas Adams"], "description": "An ordinary man is rescued from Earth moments before its demolition and travels the galaxy learning that the answer to everything is forty-two.", "genres": ["Science Fiction", "Comedy"], "categories": ["Space", "Humor", "Adventure"]},
    {"id": "book_016", "title": "Good Omens", "authors": ["Terry Pratchett", "Neil Gaiman"], "description": "An angel and a demon who have lived on Earth for thousands of years team up to prevent the apocalypse because they have grown fond of humanity.", "genres": ["Fantasy", "Comedy"], "categories": ["Humor", "Angels", "Demons"]},
    {"id": "book_017", "title": "American Gods", "authors": ["Neil Gaiman"], "description": "An ex-convict named Shadow is drawn into a conflict between old gods brought to America by immigrants and new gods of technology and media.", "genres": ["Fantasy", "Mythology"], "categories": ["Gods", "America", "Mythology"]},
    {"id": "book_018", "title": "Neverwhere", "authors": ["Neil Gaiman"], "description": "A London businessman falls through the cracks into a dark magical underworld beneath the city streets populated by strange creatures and fallen angels.", "genres": ["Fantasy", "Urban Fantasy"], "categories": ["Magic", "London", "Adventure"]},
    {"id": "book_019", "title": "The Girl with the Dragon Tattoo", "authors": ["Stieg Larsson"], "description": "A disgraced journalist and a brilliant hacker investigate the decades-old disappearance of a woman from a wealthy Swedish family.", "genres": ["Thriller", "Mystery"], "categories": ["Crime", "Hacking", "Investigation"]},
    {"id": "book_020", "title": "Gone Girl", "authors": ["Gillian Flynn"], "description": "On their wedding anniversary a man's wife disappears and he becomes the prime suspect in a psychological thriller with shocking twists.", "genres": ["Thriller", "Mystery"], "categories": ["Crime", "Psychology", "Marriage"]},
    {"id": "book_021", "title": "The Da Vinci Code", "authors": ["Dan Brown"], "description": "A symbologist and a cryptologist uncover a secret society conspiracy involving the Holy Grail hidden within the works of Leonardo da Vinci.", "genres": ["Thriller", "Mystery"], "categories": ["Crime", "Religion", "Art"]},
    {"id": "book_022", "title": "Inferno", "authors": ["Dan Brown"], "description": "Harvard professor Robert Langdon wakes with amnesia and must decode symbols based on Dante's Inferno to stop a billionaire's bioterror plot.", "genres": ["Thriller", "Mystery"], "categories": ["Crime", "History", "Art"]},
    {"id": "book_023", "title": "1984", "authors": ["George Orwell"], "description": "In a totalitarian future society a government worker begins to question the oppressive regime of Big Brother and falls in love.", "genres": ["Science Fiction", "Dystopia"], "categories": ["Politics", "Dystopia", "Surveillance"]},
    {"id": "book_024", "title": "Brave New World", "authors": ["Aldous Huxley"], "description": "In a future world where humans are engineered and conditioned for happiness a savage from a reservation challenges the foundations of civilization.", "genres": ["Science Fiction", "Dystopia"], "categories": ["Politics", "Dystopia", "Society"]},
    {"id": "book_025", "title": "The Handmaid's Tale", "authors": ["Margaret Atwood"], "description": "In a theocratic dystopia women are enslaved as reproductive servants and one woman tells the story of her resistance and survival.", "genres": ["Science Fiction", "Dystopia"], "categories": ["Politics", "Dystopia", "Feminism"]},
    {"id": "book_026", "title": "Pride and Prejudice", "authors": ["Jane Austen"], "description": "Elizabeth Bennet navigates issues of manners marriage and class in Georgian England while falling in love with the proud Mr Darcy.", "genres": ["Romance", "Classic"], "categories": ["Love", "Society", "Marriage"]},
    {"id": "book_027", "title": "Jane Eyre", "authors": ["Charlotte Bronte"], "description": "An orphaned governess falls in love with her brooding employer Mr Rochester but discovers he is hiding a dark secret in his mansion.", "genres": ["Romance", "Gothic", "Classic"], "categories": ["Love", "Mystery", "Class"]},
    {"id": "book_028", "title": "Wuthering Heights", "authors": ["Emily Bronte"], "description": "The passionate and destructive love between Catherine Earnshaw and the dark outsider Heathcliff destroys everyone around them across two generations.", "genres": ["Romance", "Gothic", "Classic"], "categories": ["Love", "Obsession", "Class"]},
    {"id": "book_029", "title": "The Alchemist", "authors": ["Paulo Coelho"], "description": "A young Andalusian shepherd travels from Spain to Egypt following his personal legend and learning that treasure lies where your heart belongs.", "genres": ["Fiction", "Inspirational"], "categories": ["Journey", "Philosophy", "Dreams"]},
    {"id": "book_030", "title": "Siddhartha", "authors": ["Hermann Hesse"], "description": "A young Indian man leaves his wealthy family to seek spiritual enlightenment through asceticism and experience arriving at his own understanding of truth.", "genres": ["Fiction", "Philosophical"], "categories": ["Spirituality", "Journey", "Philosophy"]},
    {"id": "book_031", "title": "The Shining", "authors": ["Stephen King"], "description": "A writer takes a job as winter caretaker of an isolated hotel where supernatural forces drive him to madness and violence against his family.", "genres": ["Horror"], "categories": ["Supernatural", "Psychological", "Family"]},
    {"id": "book_032", "title": "It", "authors": ["Stephen King"], "description": "A group of childhood friends are reunited as adults to battle an ancient shapeshifting evil that preys on children in the town of Derry.", "genres": ["Horror"], "categories": ["Supernatural", "Childhood", "Evil"]},
    {"id": "book_033", "title": "Dracula", "authors": ["Bram Stoker"], "description": "A Transylvanian vampire count moves to England and a small group of heroes led by Professor Van Helsing must hunt and destroy him.", "genres": ["Horror", "Gothic", "Classic"], "categories": ["Vampire", "Supernatural", "Victorian"]},
    {"id": "book_034", "title": "Frankenstein", "authors": ["Mary Shelley"], "description": "A scientist creates life from dead tissue but his creature is rejected by humanity and seeks revenge on the creator who abandoned him.", "genres": ["Horror", "Science Fiction", "Classic"], "categories": ["Science", "Supernatural", "Ethics"]},
    {"id": "book_035", "title": "The Martian", "authors": ["Andy Weir"], "description": "An astronaut is stranded alone on Mars and must use his knowledge of botany and engineering to survive until a rescue mission can reach him.", "genres": ["Science Fiction"], "categories": ["Space", "Survival", "Science"]},
    {"id": "book_036", "title": "Project Hail Mary", "authors": ["Andy Weir"], "description": "A lone astronaut wakes from a coma in deep space with no memory and must figure out his mission to save Earth from an extinction threat.", "genres": ["Science Fiction"], "categories": ["Space", "Survival", "Science"]},
    {"id": "book_037", "title": "The Hunger Games", "authors": ["Suzanne Collins"], "description": "In a dystopian future a teenage girl volunteers for a televised death match to save her sister and becomes a symbol of rebellion.", "genres": ["Science Fiction", "Dystopia", "Young Adult"], "categories": ["Survival", "Politics", "Revolution"]},
    {"id": "book_038", "title": "Catching Fire", "authors": ["Suzanne Collins"], "description": "After winning the Hunger Games Katniss Everdeen is forced back into the arena and ignites a full rebellion across the dystopian districts.", "genres": ["Science Fiction", "Dystopia", "Young Adult"], "categories": ["Survival", "Politics", "Revolution"]},
    {"id": "book_039", "title": "Ender's Game", "authors": ["Orson Scott Card"], "description": "A child military genius is trained at a battle school in space to lead humanity's defense against an alien insect species threatening extinction.", "genres": ["Science Fiction", "Young Adult"], "categories": ["Space", "War", "Strategy"]},
    {"id": "book_040", "title": "Ender's Shadow", "authors": ["Orson Scott Card"], "description": "The parallel story of Bean a street orphan who joins battle school alongside Ender and proves to be the most brilliant student of all.", "genres": ["Science Fiction", "Young Adult"], "categories": ["Space", "War", "Strategy"]},
    {"id": "book_041", "title": "The Way of Kings", "authors": ["Brandon Sanderson"], "description": "On a world battered by magical storms three characters converge on an epic conflict involving ancient knights and their bonded armor and weapons.", "genres": ["Fantasy", "Epic"], "categories": ["Magic", "War", "Adventure"]},
    {"id": "book_042", "title": "Words of Radiance", "authors": ["Brandon Sanderson"], "description": "The Knights Radiant return as the Everstorm threatens civilization and Kaladin and Shallan must master their abilities to survive.", "genres": ["Fantasy", "Epic"], "categories": ["Magic", "War", "Adventure"]},
    {"id": "book_043", "title": "Mistborn", "authors": ["Brandon Sanderson"], "description": "In a world of ash and darkness a thief with magical metal powers joins a crew to overthrow the immortal god-emperor who has ruled for a thousand years.", "genres": ["Fantasy"], "categories": ["Magic", "Revolution", "Adventure"]},
    {"id": "book_044", "title": "The Well of Ascension", "authors": ["Brandon Sanderson"], "description": "With the Lord Ruler dead the crew must defend their city against three armies while Vin struggles with her role as a mistborn hero.", "genres": ["Fantasy"], "categories": ["Magic", "War", "Politics"]},
    {"id": "book_045", "title": "Murder on the Orient Express", "authors": ["Agatha Christie"], "description": "Detective Hercule Poirot investigates a murder on a snowbound train and discovers all twelve passengers had motive to kill the victim.", "genres": ["Mystery", "Classic"], "categories": ["Crime", "Investigation", "Classic"]},
    {"id": "book_046", "title": "And Then There Were None", "authors": ["Agatha Christie"], "description": "Ten strangers are lured to an isolated island mansion and begin dying one by one according to the verses of a nursery rhyme.", "genres": ["Mystery", "Thriller", "Classic"], "categories": ["Crime", "Suspense", "Isolation"]},
    {"id": "book_047", "title": "Sherlock Holmes: A Study in Scarlet", "authors": ["Arthur Conan Doyle"], "description": "The first meeting of Dr Watson and consulting detective Sherlock Holmes as they investigate a mysterious murder in London.", "genres": ["Mystery", "Classic"], "categories": ["Crime", "Investigation", "London"]},
    {"id": "book_048", "title": "The Hound of the Baskervilles", "authors": ["Arthur Conan Doyle"], "description": "Sherlock Holmes investigates the curse of a spectral hound said to haunt the Baskerville family on the foggy moors of Devonshire.", "genres": ["Mystery", "Gothic", "Classic"], "categories": ["Crime", "Supernatural", "Investigation"]},
    {"id": "book_049", "title": "Atomic Habits", "authors": ["James Clear"], "description": "A practical guide to building good habits and breaking bad ones using the science of marginal gains and identity-based behavior change.", "genres": ["Non-fiction", "Self-help"], "categories": ["Productivity", "Psychology", "Health"]},
    {"id": "book_050", "title": "Thinking Fast and Slow", "authors": ["Daniel Kahneman"], "description": "A psychologist explains the two systems of thinking that drive human decisions revealing the biases and errors that affect judgment.", "genres": ["Non-fiction", "Psychology"], "categories": ["Psychology", "Decision Making", "Science"]},
]


@pytest.fixture
def fitted_vectorizer(tmp_path):
    v = ContentVectorizer(model_dir=str(tmp_path))
    v.fit(SAMPLE_BOOKS)
    return v


# Helpers

def top_ids(results: list) -> list[str]:
    return [r["content_id"] for r in results]


# Fit tests

def test_fit_succeeds(fitted_vectorizer):
    assert fitted_vectorizer.is_fitted


def test_fit_sets_correct_id_count(fitted_vectorizer):
    assert len(fitted_vectorizer.get_ids()) == 50


def test_fit_matrix_row_count(fitted_vectorizer):
    assert fitted_vectorizer.get_matrix().shape[0] == 50


def test_fit_vocabulary_non_empty(fitted_vectorizer):
    assert fitted_vectorizer.vocabulary_size() > 0


def test_fit_empty_raises():
    v = ContentVectorizer()
    with pytest.raises(ValueError, match="empty"):
        v.fit([])


def test_unfitted_similar_raises():
    v = ContentVectorizer()
    with pytest.raises(RuntimeError, match="not fitted"):
        v.similar("book_001")


def test_unfitted_matrix_raises():
    v = ContentVectorizer()
    with pytest.raises(RuntimeError, match="not fitted"):
        v.get_matrix()


def test_unfitted_ids_raises():
    v = ContentVectorizer()
    with pytest.raises(RuntimeError, match="not fitted"):
        v.get_ids()


def test_unfitted_vocabulary_raises():
    v = ContentVectorizer()
    with pytest.raises(RuntimeError, match="not fitted"):
        v.vocabulary_size()


# Similar tests

def test_similar_returns_correct_count(fitted_vectorizer):
    results = fitted_vectorizer.similar("book_001", top_n=5)
    assert len(results) == 5


def test_similar_excludes_self(fitted_vectorizer):
    results = fitted_vectorizer.similar("book_001", top_n=10)
    ids = top_ids(results)
    assert "book_001" not in ids


def test_similar_result_keys(fitted_vectorizer):
    results = fitted_vectorizer.similar("book_001", top_n=1)
    assert set(results[0].keys()) == {"content_id", "score", "rank"}


def test_similar_scores_between_zero_and_one(fitted_vectorizer):
    results = fitted_vectorizer.similar("book_001", top_n=10)
    for r in results:
        assert 0.0 <= r["score"] <= 1.0


def test_similar_ranks_are_sequential(fitted_vectorizer):
    results = fitted_vectorizer.similar("book_001", top_n=5)
    ranks = [r["rank"] for r in results]
    assert ranks == [1, 2, 3, 4, 5]


def test_similar_scores_descending(fitted_vectorizer):
    results = fitted_vectorizer.similar("book_001", top_n=10)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_similar_unknown_id_raises(fitted_vectorizer):
    with pytest.raises(ValueError, match="not found"):
        fitted_vectorizer.similar("nonexistent_id")


def test_similar_top_n_default(fitted_vectorizer):
    results = fitted_vectorizer.similar("book_001")
    assert len(results) == 10


def test_similar_top_n_one(fitted_vectorizer):
    results = fitted_vectorizer.similar("book_001", top_n=1)
    assert len(results) == 1


def test_similar_top_n_all(fitted_vectorizer):
    results = fitted_vectorizer.similar("book_001", top_n=49)
    assert len(results) == 49


# Semantic correctness tests

def test_harry_potter_top_result_is_chamber_of_secrets(fitted_vectorizer):
    results = fitted_vectorizer.similar("book_001", top_n=1)
    assert results[0]["content_id"] == "book_002"


def test_dune_top_result_is_dune_messiah(fitted_vectorizer):
    results = fitted_vectorizer.similar("book_005", top_n=1)
    assert results[0]["content_id"] == "book_006"


def test_shining_top_result_is_it(fitted_vectorizer):
    results = fitted_vectorizer.similar("book_031", top_n=1)
    assert results[0]["content_id"] == "book_032"


def test_enders_game_top_result_is_enders_shadow(fitted_vectorizer):
    results = fitted_vectorizer.similar("book_039", top_n=1)
    assert results[0]["content_id"] == "book_040"


def test_atomic_habits_top_result_is_thinking_fast(fitted_vectorizer):
    results = fitted_vectorizer.similar("book_049", top_n=1)
    assert results[0]["content_id"] == "book_050"


def test_thriller_books_cluster_together(fitted_vectorizer):
    thriller_ids = {"book_019", "book_020", "book_021", "book_022"}
    results = fitted_vectorizer.similar("book_019", top_n=5)
    result_ids = set(top_ids(results)[:3])
    overlap = result_ids & thriller_ids
    assert len(overlap) >= 2


def test_fantasy_books_cluster_together(fitted_vectorizer):
    fantasy_ids = {"book_001", "book_002", "book_003", "book_004", "book_011", "book_012"}
    results = fitted_vectorizer.similar("book_003", top_n=5)
    result_ids = set(top_ids(results))
    overlap = result_ids & fantasy_ids
    assert len(overlap) >= 1


def test_dystopia_books_cluster_together(fitted_vectorizer):
    dystopia_ids = {"book_023", "book_024", "book_025", "book_037", "book_038"}
    results = fitted_vectorizer.similar("book_023", top_n=5)
    result_ids = set(top_ids(results))
    overlap = result_ids & dystopia_ids
    assert len(overlap) >= 2


def test_sanderson_books_cluster_together(fitted_vectorizer):
    sanderson_ids = {"book_041", "book_042", "book_043", "book_044"}
    results = fitted_vectorizer.similar("book_041", top_n=5)
    result_ids = set(top_ids(results))
    overlap = result_ids & sanderson_ids
    assert len(overlap) >= 2


# Comics compatibility test

def test_works_with_comic_shaped_data(tmp_path):
    comics = [
        {"id": "comic_001", "title": "Batman Year One", "authors": ["Frank Miller"], "description": "Bruce Wayne returns to Gotham and becomes Batman for the first time fighting corrupt police and crime.", "genres": ["Superhero", "Crime"], "categories": ["Detective", "Dark", "Origin"]},
        {"id": "comic_002", "title": "Batman The Long Halloween", "authors": ["Jeph Loeb"], "description": "Batman hunts a serial killer called Holiday who murders on holidays in Gotham while the mob wars rage.", "genres": ["Superhero", "Mystery"], "categories": ["Detective", "Crime", "Dark"]},
        {"id": "comic_003", "title": "Spider-Man Blue", "authors": ["Jeph Loeb"], "description": "Peter Parker reflects on his early romance with Gwen Stacy and his life as Spider-Man fighting villains in New York.", "genres": ["Superhero", "Romance"], "categories": ["Adventure", "Love", "Hero"]},
    ]
    v = ContentVectorizer(model_dir=str(tmp_path))
    v.fit(comics)
    assert v.is_fitted
    results = v.similar("comic_001", top_n=2)
    assert len(results) == 2
    assert results[0]["content_id"] == "comic_002"


# Save and load tests

def test_save_creates_files(fitted_vectorizer, tmp_path):
    fitted_vectorizer.save(str(tmp_path))
    assert (tmp_path / "tfidf_vectorizer.pkl").exists()
    assert (tmp_path / "tfidf_matrix.pkl").exists()
    assert (tmp_path / "content_ids.pkl").exists()


def test_load_restores_fitted_state(fitted_vectorizer, tmp_path):
    fitted_vectorizer.save(str(tmp_path))
    v2 = ContentVectorizer(model_dir=str(tmp_path))
    v2.load(str(tmp_path))
    assert v2.is_fitted
    assert v2.get_ids() == fitted_vectorizer.get_ids()
    assert v2.vocabulary_size() == fitted_vectorizer.vocabulary_size()


def test_load_produces_same_results(fitted_vectorizer, tmp_path):
    fitted_vectorizer.save(str(tmp_path))
    v2 = ContentVectorizer(model_dir=str(tmp_path))
    v2.load(str(tmp_path))
    original = fitted_vectorizer.similar("book_001", top_n=5)
    loaded = v2.similar("book_001", top_n=5)
    assert original == loaded


def test_load_missing_file_raises(tmp_path):
    v = ContentVectorizer(model_dir=str(tmp_path))
    with pytest.raises(FileNotFoundError):
        v.load(str(tmp_path))


def test_save_unfitted_raises(tmp_path):
    v = ContentVectorizer(model_dir=str(tmp_path))
    with pytest.raises(RuntimeError, match="not fitted"):
        v.save(str(tmp_path))


# Build text tests

def test_build_text_includes_title():
    v = ContentVectorizer()
    text = v._build_text({"id": "x", "title": "Dune", "authors": [], "description": "", "genres": [], "categories": []})
    assert "dune" in text


def test_build_text_includes_authors():
    v = ContentVectorizer()
    text = v._build_text({"id": "x", "title": "", "authors": ["Frank Herbert"], "description": "", "genres": [], "categories": []})
    assert "frank herbert" in text


def test_build_text_genres_repeated():
    v = ContentVectorizer()
    text = v._build_text({"id": "x", "title": "", "authors": [], "description": "", "genres": ["Fantasy"], "categories": []})
    assert text.count("fantasy") == 2


def test_build_text_categories_repeated():
    v = ContentVectorizer()
    text = v._build_text({"id": "x", "title": "", "authors": [], "description": "", "genres": [], "categories": ["Magic"]})
    assert text.count("magic") == 2


def test_build_text_handles_missing_fields():
    v = ContentVectorizer()
    text = v._build_text({"id": "x"})
    assert isinstance(text, str)


def test_build_text_lowercased():
    v = ContentVectorizer()
    text = v._build_text({"id": "x", "title": "DUNE", "authors": [], "description": "", "genres": [], "categories": []})
    assert text == text.lower()


# is_fitted property

def test_is_fitted_false_before_fit():
    v = ContentVectorizer()
    assert v.is_fitted is False


def test_is_fitted_true_after_fit(fitted_vectorizer):
    assert fitted_vectorizer.is_fitted is True


def test_is_fitted_true_after_load(fitted_vectorizer, tmp_path):
    fitted_vectorizer.save(str(tmp_path))
    v2 = ContentVectorizer(model_dir=str(tmp_path))
    assert v2.is_fitted is False
    v2.load(str(tmp_path))
    assert v2.is_fitted is True