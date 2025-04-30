#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/time.h>
#include <sys/types.h>
#include <dirent.h>
#include <assert.h>
#include <ctype.h>
#include <zlib.h>
#include <math.h>


struct node_st
{
    int id, *fill;
    int *cost;
    struct node_st **array;
    struct node_st *left;
    struct node_st *right;
    struct node_st *up;
    int leftcost;
    int rightcost;
};

const char *outfolder;
FILE *fout;
struct node_st *tree;
char **names;
int *Kyx, *Kx, minval, bestval;
int boot, strap, n, leafs, chunks, *empty, *unique, *bootw = NULL;
int chunksize; // This needs to be defined by the user
const int GZIP_HEADER = 6;
int alternate = 0;
/*Indicates if rhm should output dot files.*/
int print_dot;
/*Indicates the name of the longest name.*/
int longest_name = 0;
/*Counter that counts the number of empty nodes present in output.*/
int *empty_counter = 0;
/*The file used tou output edge file.*/
FILE *edge_file;
/*Array containing the names for the empty nodes.*/
char **empty_names;
/*The output directory.*/
//char *dirname = "test_stemma";
/*The number of optimization iterations*/
int nb_opti_global;

void set_edge_file(char* output_file){
  edge_file = output_file;
}

void set_chuncksize(int chunkSize){
    chunksize = chunkSize;
}

void set_print_dot(int value){
    print_dot = value;
}

/*
Prints some information about the an iteration ?????
@param cmd (char): string to be included into the print. Pointer var.
*/
void usage(char *cmd)
{
  fprintf(stderr, "usage: %s <directory> <iterations> <bootstrap>\n\tdirectory -- texts (remember to align)\n\titerations -- simulated annealing iterations\n\tbootstrap -- how many bootstrap repetitions? 1 -> no bootstrap\nOutput goes to 'sankoff-tree_i.dot for i=0,...,<bootstrap-1>.\n", cmd);
  exit(-1);
}

/*Used to make drand48 work*/
#if !(_SVID_SOURCE || _XOPEN_SOURCE)
double drand48(void) {
    return rand() / (RAND_MAX + 1.0);
}
#endif

/*
Generates a random number based on the timeval from sys/time.h
*/
unsigned int set_random_seed(void)
{
  struct timeval tv;
  unsigned int seed;// unsigned -> only positive

  gettimeofday(&tv, NULL); // &ver -> gives memory address
  seed = (unsigned int) tv.tv_usec +
        (unsigned int) tv.tv_sec;

  srand(seed);

  return seed;
}

char *fullname(char *dirname, const char *fname)
{
    static char pathfname[256];

    sprintf(pathfname, "%s/%s", dirname, fname); // stores output on char buffer which are specified in sprintf
    if (strlen(pathfname) > 256)
        fprintf(stderr, "OUTCH!\n");

    return pathfname;
}

int count_lines(char *fname)
{
    FILE *f;
    int line;
    char tmp[2048];

    f = fopen(fname, "r");
    assert(f != NULL);

    line = 0;
    fgets(tmp, 2048, f);
    while (!feof(f))
    {
        line++;
        fgets(tmp, 2048, f);
    }

    fclose(f);

    return line;
}

char *str_tolower(char *str)
{
    char *ptr = str;

    while (*ptr)
    {
        *ptr = tolower(*ptr);
        ptr++;
    }

    return str;
}

int isempty(char *str)
{
    while (*str)
    {
        if (!isspace(*str))
            return 0;
        str++;
    }
    return 1;
}

int read_file(const char *dirname)
{
	DIR *dir;
  	FILE *f1, *f2;
  	gzFile gfile;
  	char buf[4096];
  	struct dirent *de;
  	int bufpos1, bufpos2, lines, f1i, f2i, ch, line;
  	long f1offset;

  	leafs = 0;
  	names = (char **) malloc(sizeof(void *) * 256);// 256 is the maximum number of names???
  	dir = (DIR *) opendir(dirname);

  	// Read names of the files.
  	while ((de = readdir(dir)))
  	{  
      const char* ext = strrchr(de->d_name, '.');
    	// Check if the file extension is .txt and file name does not contain substring edge
      if (de->d_name[0] != '.' && ext != NULL && strcmp(ext, ".txt") == 0 && strstr(de->d_name, "edge") == NULL && strstr(de->d_name, "rhm") == NULL && strstr(de->d_name, "RHM") == NULL)
    	{
      		names[leafs] = (char *) malloc(sizeof(char) * (strlen(de->d_name)+1));

          // Find the longest name
          if((strlen(de->d_name)+1) > longest_name){
            longest_name = (strlen(de->d_name)+1);
          }

      		strcpy(names[leafs], de->d_name);
      		//printf("%s ", names[leafs]);
      		leafs++;
    	}
  	}
  	printf("\n");
  	closedir(dir);

  	lines = count_lines(fullname(dirname, names[0]));

  	chunks = (lines-1)/chunksize+1; // I think this is where number of segments is calculated
  	printf("%d files, %d lines, %d chunks of size %d each.\n", 
  	leafs, lines, chunks, chunksize);

    /*
    Initializes flags and variables (Kx[f1i*chunks+ch], empty[f1i*chunks+ch], unique[f1i*chunks+ch]).
    */
  	Kyx = (int *) malloc(sizeof(int) * leafs * leafs * chunks);
  	Kx = (int *) malloc(sizeof(int) * leafs * chunks);
  	empty = (int *) malloc(sizeof(int) * leafs * chunks);
  	unique = (int *) malloc(sizeof(int) * leafs * chunks);

    /*
    Reads chunks of data from f1 and f2, processes each chunk:
      Modifies the content (buf) by replacing certain characters (& with et).
      Checks and modifies content based on defined macros (IGNORE_CASE, IGNORE_V_VS_U).
      Computes and stores sizes (Kx[f1i*chunks+ch]) of compressed data in tmp.gz.
      Calculates costs (Kyx[f1i*leafs*chunks + f2i*chunks + ch]) for data differences or exact copies.
    */
  	for (f1i = 0; f1i < leafs; f1i++)
  	{
    	f1 = fopen(fullname(dirname, names[f1i]), "r");
    	assert(f1);

    	for (ch = 0; ch < chunks; ch++)
    	{
      		Kx[f1i*chunks+ch] = -1;
      		empty[f1i*chunks+ch] = 1;
      		unique[f1i*chunks+ch] = 1;
    	}

    	for (f2i = 0; f2i < leafs; f2i++)
    	{
      		fseek(f1, 0, SEEK_SET);

      		if (f2i != f1i)
				f2 = fopen(fullname(dirname, names[f2i]), "r");
      		else
				f2 = f1;
      		assert(f2);
      
      		//printf("%s-%s:", names[f1i], names[f2i]);

      		for (ch = 0; ch < chunks; ch++)
      		{
				f1offset = ftell(f1);
				bufpos1 = 0;
				gfile = gzopen("tmp.gz", "wb");
				for (line = 0; !feof(f1) && line < chunksize; line++)
				{
	  				if (bufpos1 > 0 && buf[bufpos1-1] == '\n')
	    				buf[bufpos1-1] = ' ';
	  				fgets(buf+bufpos1, 2048-bufpos1, f1);
#ifdef REPLACE_AMP_BY_ET
	  				if (!strcmp(buf+bufpos1, "&\n"))
	    				strcpy(buf+bufpos1, "et\n");
#endif
	  				if (buf[bufpos1] && buf[bufpos1] != '\n')
	    				empty[f1i*chunks+ch] = 0;
	  				if (strcmp(buf+bufpos1, "PUUT\n") && strcmp(buf+bufpos1, "POIS\n"))
	    				bufpos1 += strlen(buf+bufpos1);
	  				else 
	    				buf[bufpos1++] = '\n';
				}
				buf[bufpos1] = '\0';

				//sort_string(buf);
				bufpos1 = strlen(buf);
				/*
				fprintf(stderr, "%s (1): length %d at #%x:\n%s\n", 
				names[f1i], bufpos1,(int)buf, buf);
				*/
				if (!bufpos1 || buf[bufpos1-1] != '\n')
	  				buf[bufpos1++]='\n';
				buf[bufpos1] = '\0';
#ifdef IGNORE_CASE
				str_tolower(buf);
#endif
#ifdef IGNORE_V_VS_U
				str_vtou(buf);
#endif

				if (Kx[f1i*chunks+ch] == -1)
				{
	  				gzputs(gfile, buf);
	  				gzflush(gfile, Z_SYNC_FLUSH);
	
	  				Kx[f1i*chunks+ch] = (int) ((struct z_stream_s *)gfile)->total_out - GZIP_HEADER;
	  				//fprintf(stderr, "%sKx=%d\n", buf,Kx[f1i * chunks + ch]);
	  				gzclose(gfile);
	  				gfile = gzopen("tmp.gz", "wb");
				}

				if (f2 == f1)
	  				fseek(f1, f1offset, SEEK_SET);
				bufpos2 = bufpos1;
				for (line = 0; !feof(f2) && line < chunksize; line++)
				{
	  				if (bufpos2 > bufpos1 && buf[bufpos2-1] == '\n')
	    				buf[bufpos2-1] = ' ';
	  				fgets(buf+bufpos2, 4096-bufpos2, f2);
	  				if (!strcmp(buf+bufpos2, "&\n"))
	    				strcpy(buf+bufpos2, "et\n");
	  				if (strcmp(buf+bufpos2, "PUUT\n") && strcmp(buf+bufpos2, "POIS\n"))
	    				bufpos2 += strlen(buf+bufpos2);
	  				else 
	    				buf[bufpos2++] = '\n';
				}
				if (bufpos2==bufpos1 || buf[bufpos2-1] != '\n')
	  				buf[bufpos2++]='\n';
				buf[bufpos2] = '\0';
#ifdef IGNORE_CASE
				str_tolower(buf+bufpos1);
#endif
#ifdef IGNORE_V_VS_U
				str_vtou(buf+bufpos1);
#endif

				/*
				fprintf(stderr, "%s-%s: at #%x and #%x:\n1:%s\n2:%s\n", 
				names[f1i], names[f2i], (int)buf, (int)(buf+bufpos1), buf, buf+bufpos1);
				*/

				//sort_string(buf+bufpos1);
				bufpos2 = bufpos1+strlen(buf+bufpos1);
				/*	
				fprintf(stderr, "%s-%s: at #%x and #%x:\n1:%s\n2:%s\n", names[f1i], names[f2i],
				(int)buf, (int)(buf+bufpos1), buf, buf+bufpos1);
				fprintf(stderr, "====%d %d ('%c')\n", bufpos2, 
				strncmp(buf, buf+bufpos1, bufpos2/2), *(buf+bufpos1+bufpos2/2-1));
				*/

				if (strncmp(buf, buf+bufpos1, bufpos2/2))
				{
	  				gzputs(gfile, buf);
	  				gzflush(gfile, Z_SYNC_FLUSH);

	  				if (1 || !isempty(buf+bufpos1))
	    				Kyx[f1i*leafs*chunks + f2i*chunks + ch] = 
	      				(int) ((struct z_stream_s *)gfile)->total_out -
	      				Kx[f1i * chunks + ch] - GZIP_HEADER;
	 				else
	  				{
	    				if (0&&f1i== 0)
	      					fprintf(stderr, "empty(%s/%d) len=%d: %s", 
		      				names[f2i], ch, strlen(buf+bufpos1), buf+bufpos1);
	    					Kyx[f1i*leafs*chunks + f2i*chunks + ch] = 0;
	  				}

	  				if (0 && f1i == f2i)
	    				fprintf(stderr, "diff %s!=%s (K(%s|%s)=%d):\n%s",
		    			names[f1i], names[f2i], names[f2i], names[f1i],
		    			Kyx[f1i*leafs*chunks + f2i*chunks+ch], buf);
				}
				else
				{
	  				/*
	  				fprintf(stderr, "%s-%s: at #%x and #%x:\n%s <- 1\n%s <- 2\n", 
		  			names[f1i], names[f2i], (int)buf, (int)(buf+bufpos1), buf, buf+bufpos1);
	  				for (bufpos1 = 0; bufpos1 < bufpos2/2; bufpos1++)
	    				fprintf(stderr, "~");
	  				fprintf(stderr, "\n");
	  				*/

#ifdef EXACT_COPY_IS_FREE
	  				Kyx[f1i*leafs*chunks + f2i*chunks + ch] = 0;
#else
	  				gzputs(gfile, buf);
	  				gzflush(gfile, Z_SYNC_FLUSH);

	  				if (1 || !isempty(buf+bufpos1))
	    				Kyx[f1i*leafs*chunks + f2i*chunks + ch] = 
	      				(int) ((struct z_stream_s *)gfile)->total_out -
	      				Kx[f1i * chunks + ch] - GZIP_HEADER;
	  				else
	  				{
	    				if (0&&f1i== 0)
	      					//fprintf(stderr, "empty(%s/%d) len=%d: %s", 
		      				//names[f2i], ch, strlen(buf+bufpos1), buf+bufpos1);
	    					Kyx[f1i*leafs*chunks + f2i*chunks + ch] = 0;
	  				}
#endif
	  				if (0 && ch == 0)
	    				fprintf(stderr, "duplicate %s=%s (K(%s|%s)=%d):\n%s",
		    			names[f1i], names[f2i], names[f2i], names[f1i],
		    			Kyx[f1i*leafs*chunks + f2i*chunks+ch], buf);
	  				if (f2i<f1i)
	    				unique[f2i*chunks+ch] = 0;
				}

				if (0 && !strcmp(names[f1i],"S") && !strcmp(names[f2i],"R"))
	  				fprintf(stderr, "%s[%d %d] K_{%d}(%s|%s)=%d.\n",
		  			buf, strncmp(buf, buf+bufpos1, bufpos2/2),
		  			isempty(buf+bufpos1), ch, names[f2i],names[f1i],
		  			Kyx[f1i*leafs*chunks+f2i*chunks+ch]);

				//printf("%d ", Kyx[f1i * leafs*chunks + f2i * chunks + ch]);

				gzclose(gfile);      
      		}
      		if (f2i != f1i)
				fclose(f2);
      		else if (0)
				fprintf(stderr, "%d %s-%s (K(%s|%s)=%d):\n%s",
				unique[f1i], names[f1i], names[f2i], names[f2i], names[f1i],
				Kyx[f1i*leafs*chunks + f2i*chunks+ch], buf);

      		//printf("\n");
    	}
    	//fprintf(stderr, ".");
    	fclose(f1);
  	}
  	//fprintf(stderr, "\n");

  	f2i = 0;
  	for (ch = 0; ch < chunks; ch++)
    	for (f1i = 0; f1i < leafs; f1i++)
      		if (unique[f1i*chunks+ch])
				f2i++;
	/*printf("%d/%d unique.\n", f2i, ch*leafs);

	printf("%dx%dx%d information array ready.\n", leafs, leafs, chunks);

	printf("'%s'(%d)->'%s'(%d)= %d\n", names[3], empty[3*chunks],
	 	names[3], empty[3*chunks], Kyx[3*leafs*chunks+3*chunks]);
  	printf("'%s'(%d)->'%s'(%d) = %d\n", names[4], empty[4*chunks],
	 	names[3], empty[3*chunks], Kyx[4*leafs*chunks+3*chunks]);
  	printf("'%s'->'%s' = %d\n", names[3], names[4], 
	 	Kyx[3*leafs*chunks+4*chunks]);
  	printf("'%s'->'%s' = %d\n", names[4], names[4],
	 	Kyx[4*leafs*chunks+4*chunks]);

  	printf("non-symmetric: %d %d\n", Kyx[3*leafs*chunks + 4*chunks],
	 	Kyx[4*leafs*chunks + 3*chunks]);*/

	/*
	for (f1i = 0; f1i < leafs; f1i++)
	{
    	Kx[f1i*chunks + ch] *= 2;
    	for (f2i = f1i+1; f2i < leafs; f2i++)
      		for (ch = 0; ch < chunks; ch++)
      		{
				Kyx[f1i*leafs*chunks + f2i*chunks + ch] =
	  			Kyx[f2i*leafs*chunks + f1i*chunks + ch] =
	  			Kyx[f1i*leafs*chunks + f2i*chunks + ch] +
	  			Kyx[f2i*leafs*chunks + f1i*chunks + ch];
      		}
  	}

  	printf("symmetric: %d %d\n", 
	 	Kyx[3*leafs*chunks + 4*chunks],
	 	Kyx[4*leafs*chunks + 3*chunks]);
  	*/

	return leafs; // Returns the number of manuscripts
}

/*
Creates a new node for a tree structure.
@param i (int): The integer value to assign to the 'id' field of the new node.
@return (struct node_st *): Returns a pointer to the newly allocated node structure.
*/
struct node_st *new_node(int i)
{
  struct node_st *new;

  new = (struct node_st *) malloc(sizeof(struct node_st));
  new->id = i;
  new->fill = (int *) malloc(sizeof(int) * chunks);
  new->left = NULL;
  new->right = NULL;
  new->up = NULL;

  return new;
}

/*
Recursively frees the memory allocated for a subtree of nodes.
@param node (struct node_st *): A pointer to the root node of the subtree to be freed.
*/
void free_subtree(struct node_st *node)
{
  if (node)
  {
    free_subtree(node->left);
    free_subtree(node->right);
    free(node->fill);
    free(node);
  }
}

/*
Frees the memory allocated for a tree structure and its associated data.
@param tree (struct node_st *): A pointer to the root node of the tree to be freed.
*/
void free_tree(struct node_st *tree)
{
  free(tree->array);
  if (tree->cost) free(tree->cost);
  free_subtree(tree);
}

/*
Recursively creates a copy of a subtree of nodes.
@param src (struct node_st *): A pointer to the root node of the subtree to be copied.
@param array (struct node_st **): An array of node pointers used for mapping copied nodes.
@return (struct node_st *): Returns a pointer to the root node of the copied subtree.
*/
struct node_st *copy_subtree(struct node_st *src, struct node_st **array)
{
  struct node_st *node;

  if (!src)
    return NULL;
  node = new_node(src->id);
  array[node->id] = node;
  node->array = array;
  node->left = copy_subtree(src->left, array);
  if (node->left)
    node->left->up = node;
  node->right = copy_subtree(src->right, array);
  if (node->right)
    node->right->up = node;

  return node;
}

/*
Creates a deep copy of a tree structure.
@param src (struct node_st *): A pointer to the root node of the tree to be copied.
@return (struct node_st *): Returns a pointer to the root node of the copied tree.
*/
struct node_st *copy_tree(struct node_st *src)
{
  struct node_st *new_tree, **array;

  array = (struct node_st **) malloc(sizeof(void *) * n);
  new_tree = copy_subtree(src, array);
  if (!src->cost)
    new_tree->cost = NULL;
  else
  {
    new_tree->cost = (int *) malloc(sizeof(int) * n*leafs*chunks*2);
    memcpy(new_tree->cost, src->cost, sizeof(int) * n*leafs*chunks*2);
  }

  return new_tree;
}

/*
Initializes the bootstrap process for data chunks.

The function initializes the bootstrap process for handling data chunks.
If the global variable 'bootw' is not already allocated, it allocates memory to store an array of integers to track counts per chunk ('chunks').
Each element in 'bootw' is initialized to zero.
If 'strap' is set to 1, each chunk is selected sequentially.
Otherwise, chunks are selected randomly using the `rand()` function.
*/
void init_bootstrap()
{
  int ch, i;

  if (!bootw)
    bootw = (int *) malloc(sizeof(int) * chunks);
  for (ch = 0; ch < chunks; ch++)
    bootw[ch] = 0;
  for (ch = 0; ch < chunks; ch++)
  {
    if (strap == 1)
      i = ch;
    else
    {
      i = -1;
      while (i < 0 || i >= chunks)
	i = (int) ((float)chunks*rand()/(RAND_MAX+1.0));
    }
    bootw[i]++;
  }
}

/*
Initializes a tree structure using a randomized or specified permutation of leaf nodes.

The function initializes a tree structure (`tree`) using a randomized or specified permutation of leaf nodes (`leafs`).
It allocates memory for an array (`array`) to map nodes by their IDs.
A permutation array (`permut`) is initialized to maintain the order of leaf nodes.
The function initializes `n` as the number of leaf nodes.

Each leaf node is assigned an ID based on a randomized or specified permutation (`pi`).
A new node (`new`) is created for each leaf node, and it is linked to its parent and the overall tree structure.
The function handles the root node (`tree`) creation and updates, ensuring correct tree structure formation.
*/
void init_tree()
{
  struct node_st *new, **array;
  int i, *permut, pi;

  tree = NULL;
  array = (struct node_st **) malloc(sizeof(void *) * (2*leafs-1));
  permut = (int *) malloc(sizeof(int) * leafs);
  for (i = 0; i < leafs; i++)
    permut[i] = i;
  n = leafs;

  for (i = 0; i < leafs; i++)
  {
    /*
    switch (i)
    {
      case 0: pi = 21; break; // BA
      case 1: pi = 34; break; // BS
      case 2: pi = 27; break; // P
      case 3: pi = 31; break; // O
      case 4: pi = 29; break; // B
      case 5: pi = 8; break; // JG
      case 6: pi = 5; break; // BLu
      case 7: pi = 19; break; // BL
      case 8: pi = 4; break; // NR2
      case 9: pi = 16; break; // JB
      default: pi = (int) ((float)(leafs-i)*rand()/(RAND_MAX+1.0));
    }
    */
    pi = (int) ((float)(leafs-i)*rand()/(RAND_MAX+1.0));
    new = new_node(permut[pi]);
    permut[pi] = permut[leafs-i-1];
    new->array = array;
    array[new->id] = new;
    if (!tree)
    {
      new->up = new_node(n++);
      new->up->array = array;
      array[new->up->id] = new->up;
      new->up->right = new;
      tree = new->up;
    }
    else
    {
      if (!tree->left)
      {
	tree->left = new;
	new->up = tree;
      }
      else
      {
	new->up = new_node(n++);
	new->up->array = array;
	array[new->up->id] = new->up;
	new->up->left = new;
	new->up->right = tree;
	tree->up = new->up;
	tree = new->up;
      }
    }
  }
  tree->cost = NULL;
  free(permut);
  fprintf(stderr, "tree with %d nodes initialized.\n", n);
}

/*
Calculates the edge label between two nodes based on shared characteristics across chunks.
@param a (struct node_st *): Pointer to the first node.
@param b (struct node_st *): Pointer to the second node.
@return sum (int): The calculated edge label value based on the shared characteristics across chunks.
*/
int edge_label(struct node_st *a, struct node_st *b)
{
  int ch, sum, ab, ba;

  sum = 0;
  for (ch = 0; ch < chunks; ch++)
  {
    if (bootw[ch])
    {
      ab = Kyx[a->fill[ch]*leafs*chunks + b->fill[ch]*chunks + ch];
      ba = Kyx[b->fill[ch]*leafs*chunks + a->fill[ch]*chunks + ch];
      if (ab < ba) sum += ab;
      else sum += ba;
    }
  }

  return sum;
}

/*
Calculates the edge length between two nodes based on their edge label and leaf penalty.
@param a (struct node_st *): Pointer to the first node.
@param b (struct node_st *): Pointer to the second node.
@return length (double): The calculated edge length.
*/
double edge_length(struct node_st *a, struct node_st *b)
{
  int leafpenalty = 0;

  return 0.7;

  if (!b->left && !b->right)
    leafpenalty = 0;
  return ((double)(edge_label(a, b)+leafpenalty+1))/60.0;
}

/*
Recursively prints the subtree rooted at the given node to the output file.
@param node (struct node_st *): Pointer to the root node of the subtree to be printed.
*/
void print_subtree(struct node_st *node)
{
  char *look, *color, *name;
  int ch;

  if (!node)
    return;

  print_subtree(node->left);
  print_subtree(node->right);

  if (node->id < leafs)
    name = names[node->id];
  else
    name = NULL;
  if (!node->up)
  {
    if (node->left && node->right)
      fprintf(fout, "%d -- %d [len=%.4f];\n", node->left->id, node->right->id,
	      edge_length(node, node->left));
    return;
  }

  look = "";
  if (node->id >= leafs)
    color = "";
#ifdef HENRIK_COLORS
  else if (name && (!strcmp(name, "A") || !strcmp(name, "Ab") || 
		    !strcmp(name, "Fg") || !strcmp(name, "H") ||
		    !strcmp(name, "Ho") || !strcmp(name, "I") ||
		    !strcmp(name, "K") || !strcmp(name, "N") ||
		    !strcmp(name, "R") || !strcmp(name, "S") ||
		    !strcmp(name, "T")))
    color = " fillcolor=lightblue"; // Finland
  else if (name && (!strcmp(name, "B") || !strcmp(name, "JG") ||
		    !strcmp(name, "FRA")))
    color = " fillcolor=khaki"; // Central Europe
  else if (name && (!strcmp(name, "AJ") || 
		    !strcmp(name, "D") || !strcmp(name, "E") ||
		    !strcmp(name, "F") || !strcmp(name, "G") ||
		    !strcmp(name, "JB") || !strcmp(name, "Li") ||
		    !strcmp(name, "LT") || !strcmp(name, "MN") ||
		    !strcmp(name, "NR") || !strcmp(name, "NR2") ||
		    !strcmp(name, "Y") || !strcmp(name, "CP")))
    color = " fillcolor=darkorange"; // Vadstena
  else
    color = " fillcolor=darkolivegreen1"; // other (mostly Sweden)
#else
  color = " fillcolor=oldlace";
#endif
  if (node->id < leafs)
    fprintf(fout, "%d [label=\"%s\"%s%s];\n", 
	    node->id, names[node->id], look, color);
  else
  {
    fprintf(fout, "%d [label=\"%s:", node->id,
	    node->id<leafs ? names[node->id] : "f");
    for (ch = 0; ch < chunks; ch++)
      if (bootw[ch])
      {
	if (empty[node->fill[ch]*chunks+ch])
	  fprintf(fout, "%s-", ch?(ch==chunks/2?"\\n":":"):"");
	else
	  fprintf(fout, "%s%s", ch?(ch==chunks/2?"\\n":":"):"", 
		  names[node->fill[ch]]);
      }
      else
	fprintf(fout, "%s_", ch?(ch==chunks/2?"\\n":":"):"");
    fprintf(fout, "\"%s];\n", look);
  }
  
  if (node->left)
    fprintf(fout, "%d -- %d [len=%.4f];\n", node->id, node->left->id,
	    edge_length(node, node->left));
  if (node->right)
    fprintf(fout, "%d -- %d [len=%.4f];\n", node->id, node->right->id,
	    edge_length(node, node->right));
}

/*
Opens an output file for writing in DOT format.

The output file is named according to the current bootstrap iteration (`boot`) 
and formatted as "rhm-tree_<boot>.dot".

The global file pointer `fout` is assigned the opened file stream.

@global fout (FILE *): Global file pointer for output file.

@sideeffects Modifies the global variable fout.
*/
void open_output(char* dirname_in)
{
  //char fname[256];
  //sprintf(fname, "rhm-tree_%d.dot", boot);
  //fout = fopen(fname, "w+");

  char fname[256];
  sprintf(fname, "%s/edges_rhm_nb_opti%d_strap_%d_chunksize_%d.dot", dirname_in, nb_opti_global, boot, chunksize);
  //printf("Output path: %s\n", fname);
  fout = fopen(fname, "w+");
}

/*
Closes the output file stream.
Ensures that any buffered data is written to the file and releases the associated resources.
@global fout (FILE *): Global file pointer for output file.
@sideeffects Closes the file stream associated with `fout`.
*/
void close_output()
{
  fclose(fout);
}

/*
Calculates the depth of the subtree rooted at the given node.
@param node (struct node_st *): Pointer to the root of the subtree.
@return (int) Depth of the subtree rooted at `node`.
*/
int depth(struct node_st *node)
{
  int dl, dr;

  if (!node)
    return 0;
  dl = depth(node->left);
  dr = depth(node->right);
  if (dl > dr)
    return dl+1;
  else
    return dr+1;
}

/*
Reorganizes the binary tree structure to make it visually balanced.

This function swaps the left and right subtrees of each node recursively 
if the left subtree has lesser depth than the right subtree.

@param node (struct node_st *): Pointer to the root of the subtree to be reorganized.
*/
void make_look_nice(struct node_st *node)
{
  struct node_st *tmp;

  if (!node)
    return;

  if (depth(node->left) < depth(node->right))
  {
    tmp = node->left;
    node->left = node->right;
    node->right = tmp;
  }

  make_look_nice(node->left);
  make_look_nice(node->right);
}

/*
Prints the binary tree structure to a DOT file for visualization.

This function first reorganizes the tree to make it visually balanced using 
the make_look_nice function. It then opens an output file in DOT format, 
prints graph information including Sankoff scores and bootstrap values, 
and finally prints the tree structure recursively using the print_subtree function.
*/
void print_tree(struct node_st *tree, char* out_file) // The first argument when it is called is a tree!!!!!!!!!!!!!!
{
  int ch;
  //fprintf(stderr, ".");
  make_look_nice(tree);
  open_output(out_file);
  fprintf(fout, "graph \"sankoff-tree\" {\nlabel=\"sankoff-score %d ", 
	  bestval);
  fprintf(fout, "bootstrap ");
  if (strap == 1)
    fprintf(fout, "off");
  else
    for (ch = 0; ch < chunks; ch++)
      fprintf(fout, "%s%d", ch?",":"", bootw[ch]);
  fprintf(fout, "\";\n");
  fprintf(fout, "edge [style=bold];\nnode[shape=plaintext fontsize=20];\n");
  print_subtree(tree);
  fprintf(fout, "}\n");
  close_output();
}

/*
Frees dynamically allocated memory used by various global arrays and pointers.

This function deallocates memory for the following global variables:
- bootw: Integer array storing bootstrap values for chunks.
- names: Array of strings storing names for leaf nodes.
- empty: Boolean array indicating if a node in the tree is empty.
- unique: Array holding unique values.
- Kx: Array storing values for Kx calculations.
- Kyx: Array storing values for Kyx calculations.
*/
void free_mem()
{
  int i;
  free(bootw);
  for (i = 0; i < leafs; i++)
    free(names[i]);
  free(names);
  free(empty);
  free(unique);
  free(Kx);
  free(Kyx);
  //free(print_dot);
}

/*
Calculates the minimum cost associated with a given node, identifier, index, and chunk.

This function calculates the minimum cost for a node in a tree based on its identifier (`id`),
index (`i`), and chunk (`ch`). It uses the global arrays `unique`, `empty`, `Kyx`, and `cost`
to determine the cost calculation logic.

@param cost (int *): Pointer to the cost array.
@param id (int): Identifier of the node.
@param i (int): Index used in calculations.
@param ch (int): Chunk index.
@return (int): Minimum cost associated with the specified parameters. If no valid cost is found,
  returns a large value (RAND_MAX/256).
*/
int min_cost(int *cost, int id, int i, int ch)
{
  int j, val, minval;

  if (!unique[i*chunks+ch])
    return RAND_MAX/256;

  if (id < leafs)
  {
#ifdef EMPTY_IS_MISSING
    if (empty[id*chunks+ch])
      return 0;
    else
#endif
      return Kyx[i*leafs*chunks+id*chunks+ch];
  }

  minval = -1;

  for (j = 0; j < leafs; j++)
  {
    if (unique[j*chunks+ch])
    {
      val = cost[j*chunks+ch] + Kyx[i*leafs*chunks+j*chunks+ch];
      if (val < minval || minval == -1)
	minval = val;
    }
  }
  
  return minval;
}

/*
Recursively evaluates the subtree starting from the given node for the specified chunk.
Updates the cost array with minimum costs for each node.
@param cost (int *): Pointer to the cost array.
@param node (struct node_st *): Pointer to the root node of the subtree to evaluate.
@param ch (int): Chunk index for which evaluation is performed.
@return (int): Minimum cost found during the evaluation of the subtree rooted at the given node.
*/
int eval_subtree(int *cost, struct node_st *node, int ch)
{
  int i, minval = 0;

  if (node->left && node->right)
  {
    eval_subtree(cost, node->left, ch);
    eval_subtree(cost, node->right, ch);
    
    for (i = 0; i < leafs; i++)
    {
      cost[node->id*leafs*chunks+i*chunks+ch] = 
	min_cost(cost+node->left->id*leafs*chunks, node->left->id, i, ch) +
	min_cost(cost+node->right->id*leafs*chunks, node->right->id, i, ch);
      if (i == 0 || isinf((float)minval) || 
	  cost[node->id*leafs*chunks+i*chunks+ch] < minval)
	minval = cost[node->id*leafs*chunks+i*chunks+ch];
    }
  }
  else
  {
    for (i = 0; i < leafs; i++)
      if (i == node->id)
	cost[node->id*leafs*chunks+i*chunks+ch] = 0.0;
      else
	cost[node->id*leafs*chunks+i*chunks+ch] = RAND_MAX/256;
    minval = 0.0;
  }

  return minval;
}

/*
Recursively evaluates the subtree rooted at the given node up to the stopper node.
Updates the cost array with minimum costs for each node.
@param tree (struct node_st *): Pointer to the root of the tree structure.
@param node (struct node_st *): Pointer to the current node being evaluated.
@param stopper (struct node_st *): Pointer to the node where evaluation should stop (exclusive).
@param ch (int): Chunk index for which evaluation is performed.
@return (int): Minimum cost found during the evaluation of the subtree up to the stopper node.
*/
int eval_uptree(struct node_st *tree, struct node_st *node, 
		struct node_st *stopper, int ch)
{
  int i, minval = 0, *cost;

  cost = tree->cost;

  if (!node)
    node = tree;

  if (node->left && node->right)
  {
    for (i = 0; i < leafs; i++)
    {
      cost[node->id*leafs*chunks+i*chunks+ch] = 
	min_cost(cost+node->left->id*leafs*chunks, node->left->id, i, ch) +
	min_cost(cost+node->right->id*leafs*chunks, node->right->id, i, ch);
      if (i == 0 || isinf((float)minval) || 
	  cost[node->id*leafs*chunks+i*chunks+ch] < minval)
	minval = cost[node->id*leafs*chunks+i*chunks+ch];
    }
  }
  else
  {
    for (i = 0; i < leafs; i++)
      if (i == node->id)
	cost[node->id*leafs*chunks+i*chunks+ch] = 0.0;
      else
	cost[node->id*leafs*chunks+i*chunks+ch] = RAND_MAX/256;
    minval = 0;
  }

  if (node->up && node->up != stopper)
    return eval_uptree(tree, node->up, stopper, ch);
  else
    return minval;
}

/*
Stores the cost values from the current node up to the root of the tree for each chunk.
The cost values are duplicated to accommodate different tree nodes sharing the same costs.
@param tree (struct node_st *): Pointer to the root of the tree structure.
@param node (struct node_st *): Pointer to the current node from where costs are stored upwards.
*/
void store_cost_uptree(struct node_st *tree, struct node_st *node)
{
  int ch, i;

  while (node)
  {
    for (ch = 0; ch < chunks; ch++)
      if (bootw[ch])
	for (i = 0; i < leafs; i++)
	  tree->cost[(n+node->id)*leafs*chunks + i*chunks+ch] =
	    tree->cost[node->id*leafs*chunks + i*chunks+ch];
    node = node->up;
  }
}

/*
Restores the cost values from the root of the tree down to the current node for each chunk.
This function reverts the cost values that were duplicated for different tree nodes.
@param tree (struct node_st *): Pointer to the root of the tree structure.
@param node (struct node_st *): Pointer to the current node where costs are restored downwards.
*/
void restore_cost_uptree(struct node_st *tree, struct node_st *node)
{
  int ch, i;

  while (node)
  {
    for (ch = 0; ch < chunks; ch++)
      if (bootw[ch])
	for (i = 0; i < leafs; i++)
	  tree->cost[node->id*leafs*chunks + i*chunks+ch] =
	    tree->cost[(n+node->id)*leafs*chunks + i*chunks+ch];
    node = node->up;
  }
}

/*
Recursively fills the subtree rooted at the given node with optimal fill values for each chunk.
The optimal fill values are determined based on the costs and relationships among nodes.
@param cost (int *): Pointer to the cost array where costs are stored.
@param node (struct node_st *): Pointer to the root node of the subtree to be filled.
*/
void fill_subtree(int *cost, struct node_st *node)
{
  int i, ch;
  int val, minval = 0;

  if (!node) return;

  for (ch = 0; ch < chunks; ch++)
  {
    if (bootw[ch])
      for (i = 0; i < leafs; i++)
      {
	if (node->up)
	  val = Kyx[node->up->fill[ch]*leafs*chunks+i*chunks+ch];
	else
	  val = Kx[i*chunks+ch];
	val += cost[node->id*leafs*chunks+i*chunks+ch];
	/*
	  if (node == node->array[19]->up && ch == 0 && 
	  (i < 8 || isinf((float)minval) || val < minval))
	  printf("for %d at %d, %d('%s%s') takes %d bytes.\n",
	  node->id, ch, i, names[i], empty[i*chunks+ch]?"/-":"", val);
	*/
	if (i == 0 || isinf((float)minval) || val < minval)
	{
	  minval = val;
	  node->fill[ch] = i;
	}
      }
  }

  fill_subtree(cost, node->left);
  fill_subtree(cost, node->right);
}

/*
Calculates the level of a node relative to the root of the tree.
@param tree (struct node_st *): Pointer to the root node of the tree.
@param node (struct node_st *): Pointer to the node for which the level is to be calculated.
@return (int): The level of the node relative to the root of the tree.
*/
int  level(struct node_st *tree, struct node_st *node)
{
  int lev = 0;

  while (node && node != tree)
  {
    node = node->up;
    lev++;
  }

  return lev;
}

/*
Evaluates the cost of a subtree or the distance between two nodes in the tree.
@param tree (struct node_st *): Pointer to the root node of the tree.
@param ra (struct node_st *): Pointer to the first node for evaluation. Can be NULL if evaluating the entire subtree.
@param rb (struct node_st *): Pointer to the second node for evaluation. Can be NULL if evaluating the entire subtree.
@return (int): The evaluated cost or distance value based on the specified nodes or subtree.
*/
int eval_tree(struct node_st *tree, struct node_st *ra,
		 struct node_st *rb)
{
  int value, ch, leva, levb;
  struct node_st *aup, *bup, *stopper;

  if (!tree->cost)
  {
    tree->cost = (int *) malloc(sizeof(int) * n*leafs*chunks*2);
    ra = rb = NULL;
  }

  value = 0.0;
  for (ch = 0; ch < chunks; ch++)
  {
    if (bootw[ch])
    {
      if (!ra && !rb)
	value += bootw[ch]*eval_subtree(tree->cost, tree, ch);
      else
      {
	leva = level(tree, ra);
	levb = level(tree, rb);
	aup = ra; bup = rb;
	while (leva > levb && aup)
	{
	  aup = aup->up;
	  leva--;
	}
	while (levb > leva && bup)
	{
	  bup = bup->up;
	  levb--;
	}
	while (aup && bup && aup != bup)
	{
	  aup = aup->up;
	  bup = bup->up;
	}
	if (aup == bup) 
	  stopper = aup;
	else
	  stopper = NULL;
	
	eval_uptree(tree, ra, stopper, ch); // not yet fully updated
	// after second call to eval_uptree, add updated value
	value += bootw[ch]*eval_uptree(tree, rb, NULL, ch); 
      }
    }
  }

  return value;
}

/*
Checks if two nodes are in the same branch of the tree.
@param a (struct node_st *): Pointer to the first node.
@param b (struct node_st *): Pointer to the second node.
@return (int): Returns 1 if both nodes are in the same branch, otherwise returns 0.
*/
int same_branch(struct node_st *a, struct node_st *b)
{
  struct node_st *node;

  if (a == b) return 1;

  node = a;
  while ((node = node->up))
    if (node == b)
      return 1;

  node = b;
  while ((node = node->up))
    if (node == a)
      return 1;

  return 0;
}

/*
Performs a mutation on a tree structure by exchanging or moving nodes 'a' and 'b'.
If 'alternate' flag is set, it exchanges the positions of 'a' and 'b' along with their parents.
Otherwise, it moves node 'a' under node 'b'.

@param tree (struct node_st *): Pointer to the root of the tree to mutate.
@param a (struct node_st *): Pointer to the first node to mutate.
@param b (struct node_st *): Pointer to the second node to mutate.
@return (struct node_st *): Pointer to the root of the mutated tree.
*/
struct node_st *do_mutate_tree(struct node_st *tree, 
			                         struct node_st *a,
			                         struct node_st *b)
{
  struct node_st *tmp;

  //oldcost = eval_tree(tree, *unra, *unrb);

  //fprintf(stderr, "1.1.1 #%d #%d #%d\n", (int)tree, (int)a, (int)b);
  //fprintf(stderr, "1.1.2 #%d #%d\n", (int)a->up, (int)b->up);

  if (alternate)
  {
    if (a->up->left == a)
      a->up->left = b;
    else 
      a->up->right = b;
    if (b->up->left == b)
      b->up->left = a;
    else
      b->up->right = a;
    
    tmp = a->up;
    a->up = b->up;
    b->up = tmp;

    //if (eval_tree(tree, *unra, *unrb) < oldcost)
    //  printf("improved by exchange (was %d).\n", oldcost);
  }
  else
  {
    /*
    fprintf(stderr, 
	    "take %d with parents %d:%d (sibling %d) and move under %d with %d.\n",
	    a->id, a->up->id, a->up->up?a->up->up->id:-1,
	    a->up->left==a?a->up->right->id:a->up->left->id,
	    b->up->id, b->id);
    */

    if (a->up->left == a)
      tmp = a->up->right;
    else
      tmp = a->up->left;
    tmp->up = a->up->up;

    if (a->up->up)
    {
      if (a->up->up->left == a->up)
	a->up->up->left = tmp;
      else
	a->up->up->right = tmp;
    }
    else
    {
      //fprintf(stderr, "%d was root, now %d.\n", a->up->id, tmp->id);
      tmp->cost = tree->cost;
      tree = tmp;
    }

    tmp = b->up;
    b->up = a->up;
    a->up->up = tmp;
    
    //fprintf(stderr, "node %d now under %d.\n", a->up->id, a->up->up->id);

    if (tmp->left == b)
      tmp->left = a->up;
    else
      tmp->right = a->up;

    a->up->left = b;
    a->up->right = a;

    //fprintf(stderr, "%d now under %d with %d (under %d).\n",
    //    a->id, a->up->id, b->id, b->up->id);

    //  if (eval_tree(tree, *unra, *unrb) < oldcost)
    //  printf("improved by joining (was %d).\n", oldcost);
  }      

  //fprintf(stderr, "1.1.x\n");

  return tree;
}

/*
Prepares nodes and subtrees for mutation in a tree structure.
Alternates between mutation strategies: either swapping nodes 'a' and 'b'
directly, or moving node 'a' under one of its sibling nodes.

@param tree (struct node_st *): Pointer to the root of the tree to mutate.
@param a (struct node_st **): Pointer to a pointer that will be set to node 'a'.
@param b (struct node_st **): Pointer to a pointer that will be set to node 'b'.
@param ra (struct node_st **): Pointer to a pointer that will be set to node 'ra'.
@param rb (struct node_st **): Pointer to a pointer that will be set to node 'rb'.
@return (struct node_st *): Pointer to the root of the mutated tree.
*/
struct node_st *prep_mutate_tree(struct node_st *tree, 
				 struct node_st **a,
				 struct node_st **b,
				 struct node_st **ra,
				 struct node_st **rb)
{
  int i, j;

  alternate = !alternate;
  //  alternate = 0;

  while (1)
  {
    i = (int) ((float)n*rand()/(RAND_MAX+1.0));
    j = (int) ((float)(n-1)*rand()/(RAND_MAX+1.0)); if (j == i) j++;
    if (i < 0 || i >=n || j < 0 || j >= n) continue;
    *a = tree->array[i];
    *b = tree->array[j];
    if ((*a)->up && (*b)->up && !same_branch(*a, *b) && 
	((*a)->up != (*b)->up) &&
	(alternate || ((*a)->up->up && (*b)->up->up)))
      break;
  }

  //fprintf(stderr, "1.1 #%d #%d #%d\n", (int)tree, (int)a->up, (int)b->up);

  //
  if (alternate)
  {
    *ra = *a;
    *rb = *b;
  }
  else
  {
    *ra = *a;
    if ((*a)->up->left == *a)
      *rb = (*a)->up->right;
    else
      *rb = (*a)->up->left;
  }

  return tree;
}

/*
Approximates the exponential function e^x for a limited range of x.

@param x (float): The exponent value.
@return (float): An approximation of e^x. Returns 0.0 if x < -3.25.
*/
float my_exp(float x)
{
  if (x < -3.25)
    return 0.0;

  x += 3.25;
  return x*x/10.5625;
}

/*
Optimizes the given tree structure using simulated annealing technique.
The optimization is performed over a specified number of iterations.

@param iters (int): Number of iterations for optimization.
@return (int): The best score achieved after optimization.
*/
int optimize_tree(int iters, char *out_file)
{
  int newval, iter, postpone = 10;
  float T, dif;
  static struct node_st *new_tree;
  struct node_st *ra, *rb, *a, *b;
#ifndef QUADRATIC_TEMP
  double alpha;
  alpha = pow(0.05, 1.0/(double)iters); // This is what defines T chage rate 
  fprintf(stderr, "alpha %f.\n", alpha);
#endif

  fprintf(stderr, "running %d iterations (tree at #%d)\n\n", iters, (int)tree);

  T = 10.0;

  iter = 0;
  bestval = minval = eval_tree(tree, NULL, NULL);
  fill_subtree(tree->cost, tree);
  if(print_dot == 1){
    print_tree(tree, out_file);
  }

  while (iter++ < iters)
  {
    if (iter > .95*iters)
      T = 0.0;
    else
#ifdef QUADRATIC_TEMP
      T = 1.0-(float)iter/(float)iters;
    T *= 5.0*T;
#else
    T = T*alpha;
#endif
#ifdef COPY_AND_REPLACE
    new_tree = prep_mutate_tree(copy_tree(tree), &a, &b, &ra, &rb);
    do_mutate_tree(new_tree, a, b);
#else
    new_tree = prep_mutate_tree(tree, &a, &b, &ra, &rb);
    store_cost_uptree(new_tree, a);
    store_cost_uptree(new_tree, b);
    do_mutate_tree(tree, a, b);
#endif
    newval = eval_tree(new_tree, ra, rb);
    if (newval <= minval 
	|| (T > 0.0 && (dif=(float)(minval-newval)/T)>-10.0 &&
	    drand48() < exp(dif)))
    {
#ifdef COPY_AND_REPLACE
      free_tree(tree);
      tree = new_tree;
#endif
      //fprintf(stderr, "accept(%d).\n", alternate);
      if (newval < bestval)
      {
	bestval = newval;
	fill_subtree(tree->cost, tree);
    if(print_dot == 1){
	    print_tree(tree, out_file);
    }
	postpone = 0;
      }
      minval = newval;
    }
    else
    {
#ifdef COPY_AND_REPLACE
      free_tree(new_tree);
#else
      // fprintf(stderr, "revert(%d) %d %d.\n", alternate, ra->id, rb->id);
      do_mutate_tree(tree, ra, rb);
      restore_cost_uptree(tree, a);
      restore_cost_uptree(tree, b);
#endif
    }

    if (!postpone)
      fprintf(stderr, 
	      "\033[1A\033[80Dbest score %d now %d (iter %d/%d temp %.2f).\n", 
	      bestval, minval, iter, iters, T);
    if (--postpone < 0)
      postpone = 250;
  }

  return bestval;
}

// Function to append a 2D array to an existing array of 2D arrays
void append2DArray(int ****arrayRef, int *size, int *capacity, int **newData, int rows, int cols) {
    // Check if we need to reallocate more space
    if (*size >= *capacity) {
        *capacity *= 2;
        *arrayRef = realloc(*arrayRef, (*capacity) * sizeof(int **));
        if (*arrayRef == NULL) {
            fprintf(stderr, "Memory allocation failed\n");
            exit(EXIT_FAILURE);
        }
    }

    // Allocate space for the new 2D array
    int **newArray = malloc(rows * sizeof(int *));
    if (newArray == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(EXIT_FAILURE);
    }

    for (int i = 0; i < rows; ++i) {
        newArray[i] = malloc(cols * sizeof(int));
        if (newArray[i] == NULL) {
            fprintf(stderr, "Memory allocation failed\n");
            exit(EXIT_FAILURE);
        }
        memcpy(newArray[i], newData[i], cols * sizeof(int));
    }

    // Append the new 2D array to the existing array
    (*arrayRef)[*size] = newArray;
    (*size)++;
}

// Function to free a 2D array
void free2DArray(int **array, int rows) {
    for (int i = 0; i < rows; ++i) {
        free(array[i]);
    }
    free(array);
}

/*
Takes 2 strings and and builds a 2D array of ASCII codes to represent each string.

@param str1 (int*): The the string that will have it's ASCII array placed at possition 0.
@param str2 (int*): The the string that will have it's ASCII array placed at possition 1.
@param length (int): The size that will be attributed for each ASCII array. Use the length of the largest string.
@return int**: An array of length 2 containing the ASCII arrays of both strings.
*/
int** build_ascii_edge(char* str1, char* str2, int length) {
    // Allocate memory for the 2D array
    int** combined_array = (int**)malloc(2 * sizeof(int*));
    if (combined_array == NULL) {
        printf("Memory allocation failed\n");
        return NULL;
    }

    // Allocate memory for each row in the 2D array
    combined_array[0] = (int*)malloc(length * sizeof(int));
    combined_array[1] = (int*)malloc(length * sizeof(int));

    // Convert each character to its ASCII code
    for (int i = 0; i < length; i++) {
        combined_array[0][i] = (int)str1[i];
         combined_array[1][i] = (int)str2[i];
    } 

    if (combined_array[0] == NULL || combined_array[1] == NULL) {
        printf("Memory allocation failed\n");
        free(combined_array[0]);
        free(combined_array[1]);
        free(combined_array);
        return NULL;
    }

     // Convert each character to its ASCII code
    for (int i = 0; i < length; i++) {
        combined_array[0][i] = (int)str1[i];
         combined_array[1][i] = (int)str2[i];
    } 

    return combined_array;
}

/*
Runs through the given tree and counts the number of edges present in the tree.

@param node (node_st*): The root of the tree to run through.
@return int: The number of edges in the tree.
*/
int countConnections(struct node_st *node) {
    if (node == NULL) {
        return 0;
    }

    // Count connections recursively
    int connections = 0;
    if (node->up != NULL) {
        connections++; // Found a connection between node and node->up
    }

    // Traverse left and right subtrees
    connections += countConnections(node->left);
    connections += countConnections(node->right);

    return connections;
}

void print2DArray(int **array, int dim1, int dim2) {
    for (int i = 0; i < dim1; ++i) {
        for (int j = 0; j < dim2; ++j) {
            printf("%d | ", array[i][j]);
        }
        printf("\n");
    }
}

/*
Traverses a tree structure and collects connections between nodes where 'up' pointers are not NULL.
@param node (struct node_st *): A pointer to the root node of the tree or subtree to traverse.
@param connections (int ****): A pointer to a pointer to an array of strings to store the connections between nodes.
@param count (int *): A pointer to an integer to store the number of connections collected.
@return None
*/
void collectConnections(struct node_st *node, char ****connections, int *count) {
    if (node == NULL) {
        return;
    }

    // Traverse left subtree
    collectConnections(node->left, connections, count);

    // If node has an 'up' pointer, add connection between node->id and node->up->id
    if (node->up != NULL) {
        char* empty_name_node_up[50];
        char* empty_name_node[50];
        sprintf(empty_name_node_up, "N_%d", node->id);
        sprintf(empty_name_node, "N_%d", node->up->id);
        fprintf(edge_file, "(%s, %s)\n", node->up->id<leafs ? names[node->up->id] : empty_name_node_up, node->id<leafs ? names[node->id] : empty_name_node);
        (*count)++;
    }

    // Traverse right subtree
    collectConnections(node->right, connections, count);
}

void open_edge()
{
  char fname[256];
  sprintf(fname, "edges_%d.txt", boot);
  edge_file = fopen(fname, "w");
}

/*
Closes the output file stream.
Ensures that any buffered data is written to the file and releases the associated resources.
@global fout (FILE *): Global file pointer for output file.
@sideeffects Closes the file stream associated with `fout`.
*/
void close_edge()
{
  fclose(edge_file);
}

/*
Builds and fill the empty_names array.
*/
void build_empty_names(){
  char nb_str[4];
  int nb_edges = countConnections(tree);
  int nb_empty = (nb_edges - leafs + 1);
  // Set empty names array
    empty_names = malloc(sizeof(char* ) * nb_edges);
    for(int i=0;i<nb_edges;i++){
      empty_names[i] = malloc(sizeof(char) * longest_name);
      if(i>=leafs){
        char empty_name[50] = "N_";
        sprintf(nb_str, "%d", i);
        strcat(empty_name, nb_str);
        empty_names[i] = empty_name;
      }
      else{
        empty_names[i] = "E";
      }

    }
}

int compute(char* dirname_in, int chunkSize, int strap, int nb_opti, int print_dot){
    nb_opti_global = nb_opti;
    set_chuncksize(chunkSize);
    set_print_dot(print_dot);
    set_random_seed();
    read_file(dirname_in);
    for (boot = 0; boot < strap; boot++)
    {
      init_bootstrap();
      init_tree();
      optimize_tree(nb_opti, dirname_in);
      if(boot < strap-1){
          free_tree(tree);
      }
    }

    return 0;

}