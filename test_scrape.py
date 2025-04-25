from scraper import scrape_bio

arbitrator_bio = scrape_bio("Jane Doe ICC arbitrator")
lawyer_bio = scrape_bio("Alex Reed Smith & Partners lawyer")

print("=== Arbitrator ===")
print(arbitrator_bio["bio"][:1000])

print("=== Lawyer ===")
print(lawyer_bio["bio"][:1000])
