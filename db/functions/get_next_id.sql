CREATE OR REPLACE FUNCTION public.get_next_id(app_label character varying, model_name character varying, min_val bigint, step bigint, max_val bigint)
 RETURNS bigint
 LANGUAGE plpgsql
AS $function$
DECLARE
  seq_name varchar(255);
  id bigint;
BEGIN
	IF max_val = 0 THEN
	  max_val = 9223372036854775807;
	END IF;
	seq_name = lower(app_label)||'_'||lower(model_name)||'_id_seq_gen';
	IF NOT EXISTS(
	    SELECT * FROM pg_class
        WHERE relkind = 'S' AND relname = seq_name)
    THEN
        EXECUTE format('CREATE SEQUENCE %1$s CYCLE INCREMENT %2$s MINVALUE %3$s MAXVALUE %4$s',
                       seq_name, step, min_val, max_val);
--        SELECT 0 INTO id;
    END IF;
    SELECT nextval(seq_name) INTO id;
    RETURN id;
END;
$function$
;
