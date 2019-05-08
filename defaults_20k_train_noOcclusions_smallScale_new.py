# Paths
# Fill this according to own setup
# Training
BACKGROUND_DIR = 'demo_data_dir/backgrounds_train_20k/'
# Validation
#BACKGROUND_DIR = 'demo_data_dir/backgrounds_val_20k/'
BACKGROUND_GLOB_STRING = '*.jpg'
POISSON_BLENDING_DIR = ''
SELECTED_LIST_FILE = 'demo_data_dir/selected.txt'
DISTRACTOR_LIST_FILE = 'demo_data_dir/neg_list.txt' 
DISTRACTOR_DIR = 'demo_data_dir/distractor_objects_dir/'
DISTRACTOR_GLOB_STRING = '*.jpg'
INVERTED_MASK = True # Set to true if white pixels represent background

# Parameters for generator
NUMBER_OF_WORKERS = 20
BLENDING_LIST = ['gaussian','poisson', 'none', 'box', 'motion']
#BLENDING_LIST = ['none', 'gaussian']

# Parameters for images
MIN_NO_OF_OBJECTS = 4
MAX_NO_OF_OBJECTS = 5
MIN_NO_OF_DISTRACTOR_OBJECTS = 0
MAX_NO_OF_DISTRACTOR_OBJECTS = 0
WIDTH = 640
HEIGHT = 480
MAX_ATTEMPTS_TO_SYNTHESIZE = 200
BACKGROUND_USES = 4

# Parameters for objects in images
MIN_SCALE = 0.7 # min scale for scale augmentation
MAX_SCALE = 1.1 # max scale for scale augmentation
MAX_DEGREES = 360 # max rotation allowed during rotation augmentation
MAX_TRUNCATION_FRACTION = 0.3 # max fraction to be truncated = MAX_TRUNCACTION_FRACTION*(WIDTH/HEIGHT)
MAX_ALLOWED_IOU = 0.3 # IOU > MAX_ALLOWED_IOU is considered an occlusion (default 0.75)
MIN_WIDTH = 6 # Minimum width of object to use for data generation
MIN_HEIGHT = 6 # Minimum height of object to use for data generation
MIN_X_POSITION = 200 # Define a rectangular area in the image where objects will end up in
MIN_Y_POSITION = 100
MAX_X_POSITION = 440
MAX_Y_POSITION = 380
