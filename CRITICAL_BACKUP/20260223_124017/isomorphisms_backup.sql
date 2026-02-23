--
-- PostgreSQL database dump
--

\restrict zDqDXRXsWMvzI6Fynh0JChv4JbKtAAoRXyAOFp28GPGV01edqtHzi4NJRoJYIHR

-- Dumped from database version 17.8 (Homebrew)
-- Dumped by pg_dump version 17.8 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: isomorphisms; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.isomorphisms VALUES (1, 'Diffusion Models (AI) ↔ MRI Diffusion (Medicine)', 'HEAT_EQUATION', '∂u/∂t = k∇²u', 'Both AI diffusion models for image generation and MRI diffusion imaging follow the same heat equation. The mathematical structure ∂u/∂t = k∇²u describes how information (AI) or water molecules (MRI) diffuse through space over time.', '{"paper_1":{"title":"Causality in Video Diffusers is Separable from Denoising","domain":"cs","arxiv_id":"2602.10095v1"},"paper_2":{"title":"Open diffusion MRI and connectivity data for epilepsy and surgery","domain":"q-bio","arxiv_id":"2602.09852v1"},"verification_method":"mathematical_structure_matching","domains":["computer_science","biology"]}', 0.90, 'verified', NULL, '2026-02-23 12:36:23.561', '2026-02-23 12:36:23.567436');
INSERT INTO public.isomorphisms VALUES (2, 'Robot Task Segmentation ↔ Sleep Stage Dynamics', 'LOTKA_VOLTERRA', 'dx/dt = ax - bxy, dy/dt = -cy + dxy', 'Robot task segmentation and sleep stage transitions both follow Lotka-Volterra dynamics. The coupled nonlinear ODEs dx/dt = ax - bxy, dy/dt = -cy + dxy describe competing states (task modes or sleep stages) with mutual inhibition.', '{"paper_1":{"title":"RoboSubtaskNet: Temporal Sub-task Segmentation for Human-to-Robot Skill Transfer","domain":"cs","arxiv_id":"2602.10015v1"},"paper_2":{"title":"Fully-automated sleep staging: multicenter validation","domain":"q-bio","arxiv_id":"2602.09793v1"},"verification_method":"mathematical_structure_matching","domains":["computer_science","biology"]}', 0.85, 'verified', NULL, '2026-02-23 12:36:23.591', '2026-02-23 12:36:23.592045');
INSERT INTO public.isomorphisms VALUES (3, 'ISING_MODEL: math ↔ q-bio', 'ISING_MODEL', 'H = -J Σ σi σj - h Σ σi', 'Both papers study binary state systems with nearest-neighbor interactions. The math paper applies this to math systems, while the q-bio paper uses the identical mathematical framework for q-bio applications. Despite the different domains, the underlying mathematics (H = -J Σ σi σj - h Σ σi) is isomorphic.', '{"paper_1":{"title":"Excursion decomposition of the XOR-Ising model","domain":"math","arxiv_id":"2602.06011v1","url":"https://arxiv.org/abs/2602.06011v1"},"paper_2":{"title":"In vitro binding energies capture Klf4 occupancy across the human genome","domain":"q-bio","arxiv_id":"2601.16151v1","url":"https://arxiv.org/abs/2601.16151v1"},"verification_method":"mathematical_structure_matching","domains":["math","q-bio"]}', 0.95, 'verified', NULL, '2026-02-23 12:36:23.593', '2026-02-23 12:36:23.593799');
INSERT INTO public.isomorphisms VALUES (4, 'POWER_LAW: physics ↔ q-fin', 'POWER_LAW', 'P(x) ∝ x^(-α)', 'Both papers study power law distributions P(x) ∝ x^(-α). The physics paper applies this to physics systems showing scale-free behavior, while the q-fin paper finds the same mathematical structure in q-fin phenomena. Despite different domains, both follow identical power law scaling.', '{"paper_1":{"title":"Compressing Complexity: A Critical Synthesis of Structural, Analytical, and Data-Driven Dimensionality Reduction in Dynamical Networks","domain":"physics","arxiv_id":"2602.00039v1","url":"https://arxiv.org/abs/2602.00039v1"},"paper_2":{"title":"A unified theory of order flow, market impact, and volatility","domain":"q-fin","arxiv_id":"2601.23172v2","url":"https://arxiv.org/abs/2601.23172v2"},"verification_method":"mathematical_structure_matching","domains":["physics","q-fin"]}', 0.90, 'verified', NULL, '2026-02-23 12:36:23.595', '2026-02-23 12:36:23.595256');
INSERT INTO public.isomorphisms VALUES (5, 'POWER_LAW: physics ↔ nlin', 'POWER_LAW', 'P(x) ∝ x^(-α)', 'Both papers study power law distributions P(x) ∝ x^(-α). The physics paper applies this to physics systems showing scale-free behavior, while the nlin paper finds the same mathematical structure in nlin phenomena. Despite different domains, both follow identical power law scaling.', '{"paper_1":{"title":"Compressing Complexity: A Critical Synthesis of Structural, Analytical, and Data-Driven Dimensionality Reduction in Dynamical Networks","domain":"physics","arxiv_id":"2602.00039v1","url":"https://arxiv.org/abs/2602.00039v1"},"paper_2":{"title":"Pattern Formation in Excitable Neuronal Maps","domain":"nlin","arxiv_id":"2601.21671v1","url":"https://arxiv.org/abs/2601.21671v1"},"verification_method":"mathematical_structure_matching","domains":["physics","nlin"]}', 0.90, 'verified', NULL, '2026-02-23 12:36:23.595', '2026-02-23 12:36:23.596235');
INSERT INTO public.isomorphisms VALUES (6, 'POWER_LAW: cond-mat ↔ q-fin', 'POWER_LAW', 'P(x) ∝ x^(-α)', 'Both papers study power law distributions P(x) ∝ x^(-α). The cond-mat paper applies this to cond-mat systems showing scale-free behavior, while the q-fin paper finds the same mathematical structure in q-fin phenomena. Despite different domains, both follow identical power law scaling.', '{"paper_1":{"title":"Broken neural scaling laws in materials science","domain":"cond-mat","arxiv_id":"2602.05702v1","url":"https://arxiv.org/abs/2602.05702v1"},"paper_2":{"title":"A unified theory of order flow, market impact, and volatility","domain":"q-fin","arxiv_id":"2601.23172v2","url":"https://arxiv.org/abs/2601.23172v2"},"verification_method":"mathematical_structure_matching","domains":["cond-mat","q-fin"]}', 0.90, 'verified', NULL, '2026-02-23 12:36:23.596', '2026-02-23 12:36:23.596786');


--
-- Name: isomorphisms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.isomorphisms_id_seq', 86, true);


--
-- PostgreSQL database dump complete
--

\unrestrict zDqDXRXsWMvzI6Fynh0JChv4JbKtAAoRXyAOFp28GPGV01edqtHzi4NJRoJYIHR

