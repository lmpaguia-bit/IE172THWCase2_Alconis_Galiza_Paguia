--
-- PostgreSQL database dump
--

\restrict q2jHHx3hUSFyxebM9FVyzoRu55Rh0XFp0WWaJAIpt3X8i6UZuAnppPDI8q8hmzW

-- Dumped from database version 18.6 (Homebrew)
-- Dumped by pg_dump version 18.4

-- Started on 2026-09-21 23:16:59 PST

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 219 (class 1259 OID 16432)
-- Name: genres; Type: TABLE; Schema: public; Owner: loey
--

CREATE TABLE public.genres (
    genre_id integer NOT NULL,
    genre_name character varying(128),
    genre_modified_on timestamp without time zone DEFAULT now(),
    genre_delete_ind boolean DEFAULT false
);


ALTER TABLE public.genres OWNER TO loey;

--
-- TOC entry 220 (class 1259 OID 16438)
-- Name: genres_genre_id_seq; Type: SEQUENCE; Schema: public; Owner: loey
--

CREATE SEQUENCE public.genres_genre_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.genres_genre_id_seq OWNER TO loey;

--
-- TOC entry 3866 (class 0 OID 0)
-- Dependencies: 220
-- Name: genres_genre_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: loey
--

ALTER SEQUENCE public.genres_genre_id_seq OWNED BY public.genres.genre_id;


--
-- TOC entry 221 (class 1259 OID 16439)
-- Name: movies; Type: TABLE; Schema: public; Owner: loey
--

CREATE TABLE public.movies (
    movie_id integer NOT NULL,
    movie_name character varying(256),
    genre_id integer,
    movie_release_date date,
    movie_delete_ind boolean DEFAULT false
);


ALTER TABLE public.movies OWNER TO loey;

--
-- TOC entry 222 (class 1259 OID 16444)
-- Name: movies_movie_id_seq; Type: SEQUENCE; Schema: public; Owner: loey
--

CREATE SEQUENCE public.movies_movie_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.movies_movie_id_seq OWNER TO loey;

--
-- TOC entry 3867 (class 0 OID 0)
-- Dependencies: 222
-- Name: movies_movie_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: loey
--

ALTER SEQUENCE public.movies_movie_id_seq OWNED BY public.movies.movie_id;


--
-- TOC entry 3700 (class 2604 OID 16445)
-- Name: genres genre_id; Type: DEFAULT; Schema: public; Owner: loey
--

ALTER TABLE ONLY public.genres ALTER COLUMN genre_id SET DEFAULT nextval('public.genres_genre_id_seq'::regclass);


--
-- TOC entry 3703 (class 2604 OID 16446)
-- Name: movies movie_id; Type: DEFAULT; Schema: public; Owner: loey
--

ALTER TABLE ONLY public.movies ALTER COLUMN movie_id SET DEFAULT nextval('public.movies_movie_id_seq'::regclass);


--
-- TOC entry 3857 (class 0 OID 16432)
-- Dependencies: 219
-- Data for Name: genres; Type: TABLE DATA; Schema: public; Owner: loey
--

INSERT INTO public.genres VALUES (1, 'Action', '2024-10-02 18:48:26.206876', false);
INSERT INTO public.genres VALUES (2, 'Drama', '2024-10-02 18:48:26.245458', false);
INSERT INTO public.genres VALUES (3, 'Horror', '2024-10-02 18:48:26.277931', false);


--
-- TOC entry 3859 (class 0 OID 16439)
-- Dependencies: 221
-- Data for Name: movies; Type: TABLE DATA; Schema: public; Owner: loey
--

INSERT INTO public.movies VALUES (2, 'Die hard', 1, '1988-07-12', false);
INSERT INTO public.movies VALUES (4, 'La La Land', 2, '2016-12-09', false);
INSERT INTO public.movies VALUES (1, 'Spider-Man: Brand New Day', 1, '2026-07-31', false);
INSERT INTO public.movies VALUES (3, 'Shake, Rattle & Roll', 3, '1984-12-25', false);
INSERT INTO public.movies VALUES (5, 'The Devil Wears Prada ', 2, '2006-06-30', false);
INSERT INTO public.movies VALUES (6, 'Sadako', 3, '2019-05-24', false);


--
-- TOC entry 3868 (class 0 OID 0)
-- Dependencies: 220
-- Name: genres_genre_id_seq; Type: SEQUENCE SET; Schema: public; Owner: loey
--

SELECT pg_catalog.setval('public.genres_genre_id_seq', 3, true);


--
-- TOC entry 3869 (class 0 OID 0)
-- Dependencies: 222
-- Name: movies_movie_id_seq; Type: SEQUENCE SET; Schema: public; Owner: loey
--

SELECT pg_catalog.setval('public.movies_movie_id_seq', 6, true);


--
-- TOC entry 3706 (class 2606 OID 16448)
-- Name: genres genres_pkey; Type: CONSTRAINT; Schema: public; Owner: loey
--

ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_pkey PRIMARY KEY (genre_id);


--
-- TOC entry 3708 (class 2606 OID 16450)
-- Name: movies movies_pkey; Type: CONSTRAINT; Schema: public; Owner: loey
--

ALTER TABLE ONLY public.movies
    ADD CONSTRAINT movies_pkey PRIMARY KEY (movie_id);


--
-- TOC entry 3709 (class 2606 OID 16451)
-- Name: movies movies_genre_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: loey
--

ALTER TABLE ONLY public.movies
    ADD CONSTRAINT movies_genre_id_fkey FOREIGN KEY (genre_id) REFERENCES public.genres(genre_id);


-- Completed on 2026-09-21 23:16:59 PST

--
-- PostgreSQL database dump complete
--

\unrestrict q2jHHx3hUSFyxebM9FVyzoRu55Rh0XFp0WWaJAIpt3X8i6UZuAnppPDI8q8hmzW

