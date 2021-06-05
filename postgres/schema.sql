--
-- Name: blacklist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.blacklist (
    id bigint NOT NULL,
    reason text
);


ALTER TABLE public.blacklist OWNER TO postgres;

--
-- Name: config; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.config (
    id bigint NOT NULL,
    prefix text,
    logid bigint,
    joinid bigint,
    joinmsg text,
    logoptions json,
    options text,
    muteid bigint
);


ALTER TABLE public.config OWNER TO postgres;

--
-- Name: mutes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mutes (
    userid bigint,
    guildid bigint,
    reason text,
    starttime timestamp without time zone,
    endtime timestamp without time zone,
    moderator bigint,
    id integer NOT NULL
);


ALTER TABLE public.mutes OWNER TO postgres;

--
-- Name: mutes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mutes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mutes_id_seq OWNER TO postgres;

--
-- Name: mutes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mutes_id_seq OWNED BY public.mutes.id;


--
-- Name: test; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.test (
    options json
);


ALTER TABLE public.test OWNER TO postgres;

--
-- Name: mutes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mutes ALTER COLUMN id SET DEFAULT nextval('public.mutes_id_seq'::regclass);


--
-- Name: blacklist blacklist_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.blacklist
    ADD CONSTRAINT blacklist_pkey PRIMARY KEY (id);


--
-- Name: config config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.config
    ADD CONSTRAINT config_pkey PRIMARY KEY (id);
