FICTION_DUMP_URL="https://libgen.is/dbdumps/fiction.rar"
LIBGEN_DUMP_URL="https://libgen.is/dbdumps/libgen.rar"
OUT_DIR=/home/vps/sql

rm -f $OUT_DIR/fiction.rar
rm -f $OUT_DIR/fiction.sql
rm -f $OUT_DIR/libgen.rar
rm -f $OUT_DIR/libgen.sql

cd $OUT_DIR
wget -c $FICTION_DUMP_URL
unrar e ./fiction.rar
rm -f $OUT_DIR/fiction.rar
mysql -u root -proot bibliomar < $OUT_DIR/fiction.sql
rm -f $OUT_DIR/fiction.sql

wget -c $LIBGEN_DUMP_URL
unrar e ./libgen.rar
rm -f $OUT_DIR/libgen.rar
mysql -u root -proot bibliomar < $OUT_DIR/libgen.sql
rm -f $OUT_DIR/libgen.sql

sudo -u manticore indexer --rotate --all