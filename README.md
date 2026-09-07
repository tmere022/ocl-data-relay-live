# OCL Data Relay (Live)

Automated validated mirror of the Office of the Commissioner of Lobbying of Canada public bulk datasets.

The inherited GitHub Actions scheduler runs daily. It downloads both official archives into temporary storage, performs full ZIP CRC and required-file validation, publishes an immutable release, and only then commits manifest.json. Consumers verify byte size and SHA-256 before installing.

Public source catalogues:
- Communications: https://open.canada.ca/data/en/dataset/a34eb330-7136-4f5e-9f5f-3ba41df58b06
- Registrations: https://open.canada.ca/data/en/dataset/70ef2117-1095-4d77-80eb-b87f2bada2a4
