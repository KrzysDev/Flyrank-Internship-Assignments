# Prompt Iteration Log — FL-01 Target Task

**Task chosen:** Creating a first-person player movement controller script for Unity (C#).
**Models compared:** ChatGPT vs Claude
**Technique progression:** Naive prompt → Role assignment + clearer goal → Added context/motivation → Few-shot examples (output criteria) → Output structure constraint → Step decomposition (planning step)

---

## Iteration 1 — Naive Prompt

**Technique:** None (baseline)

**Prompt:**
```
Create a first person controller script for a unity game
```

### Output — ChatGPT
```csharp
using UnityEngine;

[RequireComponent(typeof(CharacterController))]
public class FirstPersonController : MonoBehaviour
{
    [Header("Movement Settings")]
    [SerializeField] private float walkSpeed = 5f;
    [SerializeField] private float runSpeed = 8f;
    [SerializeField] private float jumpHeight = 2f;
    [SerializeField] private float gravity = -9.81f;

    [Header("Look Settings")]
    [SerializeField] private float mouseSensitivity = 2f;
    [SerializeField] private float lookXLimit = 80f;

    private CharacterController characterController;
    private Camera playerCamera;
    private Vector3 moveDirection = Vector3.zero;
    private float rotationX = 0f;
    private bool isRunning = false;

    private void Awake()
    {
        characterController = GetComponent<CharacterController>();
        playerCamera = GetComponentInChildren<Camera>();

        // Lock and hide cursor
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
    }

    private void Update()
    {
        HandleMovement();
        HandleMouseLook();
    }

    private void HandleMovement()
    {
        // Check if player is grounded
        bool isGrounded = characterController.isGrounded;

        // Get input
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");

        // Running with Left Shift
        isRunning = Input.GetKey(KeyCode.LeftShift);

        float currentSpeed = isRunning ? runSpeed : walkSpeed;

        // Calculate movement direction in local space
        Vector3 forward = transform.TransformDirection(Vector3.forward);
        Vector3 right = transform.TransformDirection(Vector3.right);

        // Movement vector
        float targetMoveSpeed = (horizontal * currentSpeed) + (vertical * currentSpeed);
        moveDirection = (forward * vertical + right * horizontal) * currentSpeed;

        // Jumping
        if (isGrounded && Input.GetButtonDown("Jump"))
        {
            moveDirection.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
        }

        // Apply gravity
        if (!isGrounded)
        {
            moveDirection.y += gravity * Time.deltaTime;
        }
        else if (moveDirection.y < 0)
        {
            moveDirection.y = -2f; // Slight downward force when grounded
        }

        // Move the character
        characterController.Move(moveDirection * Time.deltaTime);
    }

    private void HandleMouseLook()
    {
        // Get mouse input
        float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
        float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;

        // Rotate horizontally (body)
        transform.Rotate(0, mouseX, 0);

        // Rotate vertically (camera)
        rotationX -= mouseY;
        rotationX = Mathf.Clamp(rotationX, -lookXLimit, lookXLimit);
        playerCamera.transform.localRotation = Quaternion.Euler(rotationX, 0, 0);
    }

    // Optional: Public method to unlock cursor (e.g., for menus)
    public void UnlockCursor()
    {
        Cursor.lockState = CursorLockMode.None;
        Cursor.visible = true;
    }
}
```
**FirstPersonController.cs** has been created for your Unity project.

### How to Use It
1. Create a **Player** GameObject (typically a Capsule).
2. Add the **CharacterController** component to it (the script requires it).
3. Add a **Camera** as a child of the Player (positioned at eye height, e.g., Y = 1.6–1.8).
4. Attach the `FirstPersonController` script to the Player GameObject.
5. Play the scene.

### Controls
- **WASD** — Move
- **Left Shift** — Run
- **Space** — Jump
- **Mouse** — Look around
- Cursor is automatically locked/hidden during play.

### Features
- Smooth mouse look with vertical clamping
- Walking + running
- Jumping with realistic gravity
- Proper ground detection via CharacterController
- Works well with standard Unity physics/colliders

### Customization
All main settings are exposed in the Inspector under **Movement Settings** and **Look Settings**.

Would you like any modifications? For example:
- Add crouching
- Add head bob / footsteps sounds
- Add sprint stamina
- Switch to Rigidbody-based physics
- Add slope handling / ledge grabbing

Just let me know!

### Output — Claude
Here's a standard first-person controller script for Unity using the CharacterController component:

```csharp
using UnityEngine;

[RequireComponent(typeof(CharacterController))]
public class FirstPersonController : MonoBehaviour
{
    [Header("Movement")]
    public float walkSpeed = 5f;
    public float sprintSpeed = 8f;
    public float crouchSpeed = 2.5f;
    public float jumpHeight = 1.5f;
    public float gravity = -19.62f; // ~2x normal for snappier feel

    [Header("Mouse Look")]
    public float mouseSensitivity = 2f;
    public float maxLookAngle = 90f;
    public bool invertY = false;

    [Header("Crouch")]
    public float standingHeight = 2f;
    public float crouchingHeight = 1f;
    public float crouchTransitionSpeed = 10f;

    [Header("References")]
    public Transform cameraHolder; // Empty GameObject at eye level, holds the Camera

    private CharacterController controller;
    private Vector3 velocity;
    private float verticalRotation = 0f;
    private bool isCrouching = false;
    private float targetHeight;
    private Vector3 originalCameraLocalPos;

    void Start()
    {
        controller = GetComponent<CharacterController>();
        targetHeight = standingHeight;

        if (cameraHolder != null)
            originalCameraLocalPos = cameraHolder.localPosition;

        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
    }

    void Update()
    {
        HandleMouseLook();
        HandleMovement();
        HandleCrouch();

        // Toggle cursor lock with Escape (useful for testing)
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            Cursor.lockState = Cursor.lockState == CursorLockMode.Locked
                ? CursorLockMode.None
                : CursorLockMode.Locked;
            Cursor.visible = !Cursor.visible;
        }
    }

    void HandleMouseLook()
    {
        float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
        float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity * (invertY ? 1 : -1);

        // Rotate the body left/right
        transform.Rotate(Vector3.up * mouseX);

        // Rotate the camera up/down, clamped
        verticalRotation += mouseY;
        verticalRotation = Mathf.Clamp(verticalRotation, -maxLookAngle, maxLookAngle);

        if (cameraHolder != null)
            cameraHolder.localEulerAngles = new Vector3(verticalRotation, 0f, 0f);
    }

    void HandleMovement()
    {
        bool isGrounded = controller.isGrounded;

        if (isGrounded && velocity.y < 0)
            velocity.y = -2f; // small downward force to keep grounded

        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");

        Vector3 move = transform.right * horizontal + transform.forward * vertical;
        move = Vector3.ClampMagnitude(move, 1f);

        float currentSpeed = walkSpeed;
        if (isCrouching)
            currentSpeed = crouchSpeed;
        else if (Input.GetKey(KeyCode.LeftShift))
            currentSpeed = sprintSpeed;

        controller.Move(move * currentSpeed * Time.deltaTime);

        // Jump
        if (Input.GetButtonDown("Jump") && isGrounded && !isCrouching)
        {
            velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
        }

        velocity.y += gravity * Time.deltaTime;
        controller.Move(velocity * Time.deltaTime);
    }

    void HandleCrouch()
    {
        if (Input.GetKeyDown(KeyCode.LeftControl) || Input.GetKeyDown(KeyCode.C))
        {
            isCrouching = !isCrouching;
        }

        targetHeight = isCrouching ? crouchingHeight : standingHeight;

        controller.height = Mathf.Lerp(controller.height, targetHeight, Time.deltaTime * crouchTransitionSpeed);

        // Keep the controller's center aligned so it doesn't sink into the floor
        Vector3 center = controller.center;
        center.y = controller.height / 2f;
        controller.center = center;

        // Adjust camera holder height to match crouch, if assigned
        if (cameraHolder != null)
        {
            Vector3 camPos = originalCameraLocalPos;
            camPos.y = originalCameraLocalPos.y - (standingHeight - controller.height);
            cameraHolder.localPosition = Vector3.Lerp(cameraHolder.localPosition, camPos, Time.deltaTime * crouchTransitionSpeed);
        }
    }
}
```

**Setup instructions:**
1. Create an empty GameObject as your player, add a `CharacterController` component to it, and attach this script.
2. Create an empty child GameObject named "CameraHolder" positioned at roughly eye level (e.g., `y = 1.6`).
3. Parent your Main Camera to "CameraHolder".
4. Drag the "CameraHolder" object into the `cameraHolder` field in the inspector.
5. Adjust `walkSpeed`, `sprintSpeed`, `mouseSensitivity`, etc. to taste.

**Notes:**
- Uses Unity's legacy Input Manager (`Input.GetAxis`). If your project uses the newer Input System package, let me know and I can rewrite it with `InputAction`s instead.
- Gravity is doubled from real-world for a snappier, more "game-like" jump feel — tune `gravity` and `jumpHeight` together if it feels off.
- Crouching smoothly lerps both collider height and camera position.

Want me to add features like head bobbing, footstep sounds, leaning, or a stamina system for sprinting?

### Note on this iteration (both models)

- **ChatGPT:** Produced a functional, well-organized controller with clean movement/look separation and a reasonably helpful post-answer explanation (setup steps, controls list, feature summary). However, it invented redundant code (`targetMoveSpeed` is calculated but never used), scattered obvious comments (`// Get input`, `// Move the character`) on self-explanatory lines, and used a "run" terminology instead of the more standard "sprint," which is a minor naming inconsistency with common FPS conventions.
- **Claude:** Went further than requested by adding a full crouch system (height lerping, camera offset compensation, cursor-lock toggle on Escape) — none of which were asked for. It defaulted to `public` fields instead of `[SerializeField] private`, which is worse encapsulation practice than ChatGPT's version. It also hardcoded camera rotation logic directly into the movement script rather than separating concerns, and its inline comments (`// Rotate the body left/right`) explain trivial lines unnecessarily.
- **Takeaway:** Without constraints, both models over-deliver in different directions — ChatGPT over-engineers structurally (dead code), Claude over-engineers in scope (unrequested crouch feature) and under-delivers on field encapsulation. Neither respects the principle of building only what was asked.

---

## Iteration 2 — Role Assignment + Clearer Goal

**Technique:** Role assignment (senior Unity developer persona) + explicit, scoped goal

**Prompt:**
```
You are senior Unity Game Developer. You know about every important aspect of creating a game
such as clean code principles. Your goal is to create player movement script for first person
game. Include walking in every direction, jumping and sprinting.
```

### Output — ChatGPT
```csharp
using UnityEngine;

/// <summary>
/// Senior-grade First-Person Controller for Unity.
/// Features:
/// - Smooth WASD movement (all directions)
/// - Sprinting (Left Shift - hold)
/// - Jumping with realistic physics
/// - Mouse look with vertical clamping
/// - Clean, maintainable, and extensible code following SOLID principles
/// - Uses CharacterController for reliable collision handling
///
/// Setup Instructions:
/// 1. Create an empty GameObject named "Player"
/// 2. Add CharacterController component
/// 3. Add this script to the Player
/// 4. Create a Camera as a child of Player (position it at eye height, e.g. (0, 1.6, 0))
/// 5. Assign the child Camera to the "Player Camera" field in Inspector
/// 6. (Optional) Add a capsule collider mesh as visual for the player body
/// </summary>
[RequireComponent(typeof(CharacterController))]
public class FirstPersonController : MonoBehaviour
{
    [Header("Movement Settings")]
    [Tooltip("Base walking speed in m/s")]
    [SerializeField] private float walkSpeed = 5f;

    [Tooltip("Sprint speed multiplier (hold Left Shift)")]
    [SerializeField] private float sprintMultiplier = 1.8f;

    [Tooltip("How high the player can jump (in meters)")]
    [SerializeField] private float jumpHeight = 2f;

    [Header("Look Settings")]
    [Tooltip("Mouse sensitivity for looking around")]
    [SerializeField] private float mouseSensitivity = 120f;

    [Tooltip("Reference to the camera (usually a child of this GameObject)")]
    [SerializeField] private Transform playerCamera;

    [Header("Grounding & Physics")]
    [Tooltip("Extra downward force when grounded to stick to slopes")]
    [SerializeField] private float groundStickForce = -2f;

    [Tooltip("Gravity multiplier (Earth is -9.81)")]
    [SerializeField] private float gravity = -9.81f;

    // Component references
    private CharacterController controller;

    // State
    private Vector3 velocity;
    private float xRotation = 0f;
    private bool isSprinting;

    // Input caching (for better performance and readability)
    private float horizontalInput;
    private float verticalInput;
    private float mouseX;
    private float mouseY;

    private void Awake()
    {
        controller = GetComponent<CharacterController>();

        // Auto-assign main camera if not set
        if (playerCamera == null)
        {
            playerCamera = Camera.main.transform;
            Debug.LogWarning("Player Camera not assigned. Using Camera.main.");
        }

        // Lock cursor for FPS experience
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
    }

    private void Update()
    {
        HandleInput();
        HandleMovement();
        HandleLooking();
    }

    private void HandleInput()
    {
        // Movement input
        horizontalInput = Input.GetAxisRaw("Horizontal");
        verticalInput = Input.GetAxisRaw("Vertical");

        // Sprint (hold)
        isSprinting = Input.GetKey(KeyCode.LeftShift);

        // Mouse look
        mouseX = Input.GetAxis("Mouse X");
        mouseY = Input.GetAxis("Mouse Y");
    }

    private void HandleMovement()
    {
        // Ground check
        bool isGrounded = controller.isGrounded;

        // Reset vertical velocity when grounded (with small downward force for slopes)
        if (isGrounded && velocity.y < 0f)
        {
            velocity.y = groundStickForce;
        }

        // Calculate current speed
        float currentSpeed = isSprinting ? walkSpeed * sprintMultiplier : walkSpeed;

        // Direction relative to player orientation (not camera)
        Vector3 moveDirection = transform.right * horizontalInput + transform.forward * verticalInput;

        // Normalize only if moving diagonally (prevents faster diagonal movement)
        if (moveDirection.sqrMagnitude > 1f)
        {
            moveDirection.Normalize();
        }

        // Horizontal movement
        controller.Move(moveDirection * currentSpeed * Time.deltaTime);

        // Jumping
        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            // Physics-based jump velocity: v = sqrt(2 * h * g)
            velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
        }

        // Apply gravity
        velocity.y += gravity * Time.deltaTime;

        // Vertical movement
        controller.Move(velocity * Time.deltaTime);
    }

    private void HandleLooking()
    {
        // Horizontal rotation (whole player body)
        float bodyRotation = mouseX * mouseSensitivity * Time.deltaTime;
        transform.Rotate(Vector3.up * bodyRotation);

        // Vertical rotation (camera only)
        xRotation -= mouseY * mouseSensitivity * Time.deltaTime;
        xRotation = Mathf.Clamp(xRotation, -85f, 85f); // Prevent over-rotation

        playerCamera.localRotation = Quaternion.Euler(xRotation, 0f, 0f);
    }

    // Optional: Public methods for external systems (e.g. UI, power-ups, etc.)
    public float GetCurrentSpeed() => isSprinting ? walkSpeed * sprintMultiplier : walkSpeed;
    public bool IsGrounded() => controller.isGrounded;
    public bool IsSprinting() => isSprinting;

    // Clean up cursor when script is disabled
    private void OnDisable()
    {
        Cursor.lockState = CursorLockMode.None;
        Cursor.visible = true;
    }
}
```

### Key Design Decisions (Senior Dev Perspective):
1. **Clean Code**: Separated concerns into small, single-responsibility methods.
2. **Inspector-Friendly**: All important values exposed with tooltips and headers.
3. **Performance**: Using `GetAxisRaw` for snappier response and caching input.
4. **Physics Accuracy**: Proper jump velocity calculation + ground sticking.
5. **Extensibility**: Easy to add crouching, leaning, stamina for sprint, footstep sounds, etc.
6. **Robustness**: Handles missing camera gracefully and clamps vertical look.

**Recommended Enhancements (Next Steps)**:
- Add stamina system for sprinting
- Footstep audio + head bob
- Slope limit handling (already decent with CharacterController)
- Input System package integration for better input management

Drop this script in and you should have a solid FPS foundation! Let me know if you want the advanced version with stamina, procedural head bob, or Input System support.

### Output — Claude
# First Person Player Movement (Unity)

Here's a clean, well-structured first-person movement controller using Unity's `CharacterController` component — the standard approach for FPS-style movement (avoids physics jitter you'd get with Rigidbody).

## Setup
1. Add a `CharacterController` component to your Player GameObject.
2. Attach the script below to that same GameObject.
3. Assign a `Transform` for the camera (child object at eye height) to `cameraTransform` if you also want mouse look — I've included a basic mouse-look toggle, but focus is on movement.

```csharp
using UnityEngine;

[RequireComponent(typeof(CharacterController))]
public class FirstPersonMovement : MonoBehaviour
{
    [Header("Movement Settings")]
    [SerializeField] private float walkSpeed = 4.5f;
    [SerializeField] private float sprintSpeed = 8f;
    [SerializeField] private float acceleration = 12f;

    [Header("Jump Settings")]
    [SerializeField] private float jumpHeight = 1.2f;
    [SerializeField] private float gravity = -18f;
    [SerializeField] private int maxJumps = 1; // set to 2 for double jump

    [Header("Ground Check")]
    [SerializeField] private float groundedStickForce = -2f;

    [Header("Input Keys")]
    [SerializeField] private KeyCode sprintKey = KeyCode.LeftShift;
    [SerializeField] private KeyCode jumpKey = KeyCode.Space;

    private CharacterController controller;
    private Vector3 velocity;
    private Vector3 currentMoveVelocity;
    private int jumpsRemaining;
    private bool isGrounded;

    private void Awake()
    {
        controller = GetComponent<CharacterController>();
    }

    private void Update()
    {
        HandleGroundCheck();
        HandleMovement();
        HandleJump();
        ApplyGravity();
    }

    private void HandleGroundCheck()
    {
        isGrounded = controller.isGrounded;

        if (isGrounded)
        {
            jumpsRemaining = maxJumps;

            // Small downward force to keep controller "stuck" to ground
            if (velocity.y < 0f)
                velocity.y = groundedStickForce;
        }
    }

    private void HandleMovement()
    {
        float horizontalInput = Input.GetAxisRaw("Horizontal"); // A/D
        float verticalInput = Input.GetAxisRaw("Vertical");     // W/S

        Vector3 inputDirection = (transform.right * horizontalInput + transform.forward * verticalInput);
        inputDirection = Vector3.ClampMagnitude(inputDirection, 1f); // prevent faster diagonal movement

        float targetSpeed = Input.GetKey(sprintKey) ? sprintSpeed : walkSpeed;
        Vector3 targetVelocity = inputDirection * targetSpeed;

        // Smooth acceleration/deceleration for less robotic feel
        currentMoveVelocity = Vector3.MoveTowards(currentMoveVelocity, targetVelocity, acceleration * Time.deltaTime * targetSpeed);

        controller.Move(currentMoveVelocity * Time.deltaTime);
    }

    private void HandleJump()
    {
        if (Input.GetKeyDown(jumpKey) && jumpsRemaining > 0)
        {
            velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
            jumpsRemaining--;
        }
    }

    private void ApplyGravity()
    {
        velocity.y += gravity * Time.deltaTime;
        controller.Move(velocity * Time.deltaTime);
    }

    // Public getters — useful for animation/sound scripts to react to state
    public bool IsGrounded => isGrounded;
    public bool IsSprinting => Input.GetKey(sprintKey) && currentMoveVelocity.sqrMagnitude > 0.1f;
    public float CurrentSpeed => currentMoveVelocity.magnitude;
}
```

## Why this structure
- **Single Responsibility per method** — `HandleGroundCheck`, `HandleMovement`, `HandleJump`, `ApplyGravity` are each self-contained, so you can easily extend (e.g., add crouching) without untangling logic.
- **Serialized fields with `[Header]`** — designer-friendly tuning in the Inspector without touching code.
- **`Vector3.MoveTowards` for acceleration** — avoids the "instant stop/start" feel of raw input, without needing full physics simulation.
- **Separate gravity from jump velocity** — keeps falling behavior realistic and consistent whether the player jumped or walked off a ledge.
- **`jumpsRemaining`** — built in so double-jump is a one-line change (`maxJumps = 2`), rather than a rewrite.
- **Public read-only properties** (`IsGrounded`, `IsSprinting`, `CurrentSpeed`) — lets an Animator Controller or audio script read state without duplicating logic or tightly coupling to input code.

## A couple of things worth adding next
- **Mouse look script** (separate component) — camera rotation should stay decoupled from movement for clean separation of concerns.
- **Input System package** — if you want gamepad support or rebindable keys, migrating from the legacy `Input` class to Unity's new Input System is the modern approach.
- **Slope handling** — `CharacterController` handles most slopes fine by default, but very steep slopes may need a `slopeLimit` tweak on the component itself.

Want me to add mouse look, crouching, or a state machine (Idle/Walk/Sprint/Air) to layer on top of this?

### Note on this iteration (both models)

- **ChatGPT:** Adopted the "senior developer" framing mostly at the level of surface polish — XML doc comments, `[Tooltip]` attributes, and a "Key Design Decisions" section styled like a code review summary. It still kept mouse look bundled into the same script even though only movement was requested, and left several obvious inline comments (`// Movement input`, `// Mouse look`) that a senior dev wouldn't write. It also introduced an unused pattern (`GetCurrentSpeed()`, `IsSprinting()`) duplicating logic already present in private fields.
- **Claude:** Correctly separated movement from mouse look (explicitly said "focus is on movement" and mouse look is optional/separate), used `[SerializeField] private` consistently — better encapsulation than iteration 1. It still added a double-jump scaffold (`maxJumps`) that wasn't requested, showing it's still guessing at "senior dev" extensibility rather than strictly scoping to the ask. Comments were more purposeful (explaining *why*, e.g. the acceleration line) rather than restating *what*.
- **Takeaway:** The role assignment nudged both models toward more "professional" formatting (headers, tooltips, serialized fields) but did not stop either from padding the scope with unrequested systems (ChatGPT's helper methods, Claude's double jump). Claude respected separation of concerns (movement vs. camera) noticeably better than ChatGPT in this round.

---

## Iteration 3 — Added Context and Motivation

**Technique:** Context and motivation (game concept, setting, tone) layered onto the role-assignment prompt

**Prompt:**
```
I have a dream of creating a fast-paced shooter game like Doom. My game will be about a hero
who's goal is to save solar system from malicious Aliens. The fight will occur on an spaceship.

You are senior Unity Game Developer. You know about every important aspect of creating a game
such as clean code principles. Your goal is to create player movement script for first person
game. Include walking in every direction, jumping and sprinting.
```

### Output — ChatGPT
```csharp
using UnityEngine;

/// <summary>
/// First-person player movement controller optimized for fast-paced shooter gameplay (Doom-like).
/// Features: WASD movement (all directions), sprint (Left Shift), jump (Space), and smooth mouse look.
/// Uses CharacterController for reliable collision and ground detection on spaceship floors/walls.
/// </summary>
[RequireComponent(typeof(CharacterController))]
public class PlayerMovement : MonoBehaviour
{
    [Header("Movement Settings")]
    [Tooltip("Base walking speed in m/s")]
    public float walkSpeed = 6f;

    [Tooltip("Sprint speed multiplier (hold Left Shift)")]
    public float sprintMultiplier = 1.6f;

    [Tooltip("How high the player can jump")]
    public float jumpHeight = 1.8f;

    [Header("Mouse Look Settings")]
    [Tooltip("Mouse sensitivity for looking around")]
    public float mouseSensitivity = 120f;

    [Tooltip("Reference to the camera (usually a child of the player)")]
    public Transform playerCamera;

    [Header("Physics")]
    public float gravity = -19.62f; // Stronger gravity for snappy Doom-like feel

    // Private fields
    private CharacterController controller;
    private Vector3 velocity;
    private float xRotation = 0f;
    private bool isGrounded;

    private void Awake()
    {
        controller = GetComponent<CharacterController>();

        // Auto-assign camera if not set (common hierarchy: Player > Camera)
        if (playerCamera == null)
        {
            playerCamera = GetComponentInChildren<Camera>()?.transform;
            if (playerCamera == null)
            {
                Debug.LogError("PlayerCamera not assigned and no Camera found as child!");
            }
        }

        // Hide and lock cursor for FPS experience
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
    }

    private void Update()
    {
        HandleMouseLook();
        HandleMovement();
    }

    private void HandleMouseLook()
    {
        float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity * Time.deltaTime;
        float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity * Time.deltaTime;

        // Vertical rotation (pitch) on camera
        xRotation -= mouseY;
        xRotation = Mathf.Clamp(xRotation, -85f, 85f); // Prevent over-rotation

        playerCamera.localRotation = Quaternion.Euler(xRotation, 0f, 0f);

        // Horizontal rotation (yaw) on player body
        transform.Rotate(Vector3.up * mouseX);
    }

    private void HandleMovement()
    {
        // Ground check
        isGrounded = controller.isGrounded;

        if (isGrounded && velocity.y < 0f)
        {
            velocity.y = -2f; // Small downward force to stick to ground
        }

        // Get input (normalized for diagonal movement)
        float moveX = Input.GetAxisRaw("Horizontal");
        float moveZ = Input.GetAxisRaw("Vertical");

        Vector3 moveDirection = transform.right * moveX + transform.forward * moveZ;
        moveDirection.Normalize(); // Prevent faster diagonal movement

        // Sprint logic
        float currentSpeed = walkSpeed;
        if (Input.GetKey(KeyCode.LeftShift) && moveDirection.sqrMagnitude > 0.01f)
        {
            currentSpeed = walkSpeed * sprintMultiplier;
        }

        // Move horizontally
        controller.Move(moveDirection * currentSpeed * Time.deltaTime);

        // Jumping
        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
        }

        // Apply gravity
        velocity.y += gravity * Time.deltaTime;

        // Move vertically (gravity + jump)
        controller.Move(velocity * Time.deltaTime);
    }

    /// <summary>
    /// Optional: Call this from other scripts to temporarily disable movement (e.g., during cutscenes or death).
    /// </summary>
    public void SetMovementEnabled(bool enabled)
    {
        enabled = enabled; // Can be used to toggle input processing if you expand the class
    }
}
```

### Setup Instructions (Unity Editor)
1. Create an empty GameObject named `Player`.
2. Add the `CharacterController` component to it.
3. Add a child GameObject named `Main Camera` (or any name) with a Camera component.
4. Attach this `PlayerMovement` script to the `Player` object.
5. Drag the Camera into the `Player Camera` field in the Inspector.
6. (Optional) Add a Capsule Collider shape visually for debugging, but CharacterController handles collisions.

### Why this design is clean & performant
- **Single Responsibility**: Only handles movement + looking.
- **Fast-paced feel**: Strong gravity, responsive input, sprint multiplier.
- **Doom-like**: Snappy jumping, no inertia/sliding by default (CharacterController).
- **Extensible**: Easy to add crouch, leaning, head bob, footsteps, etc. later.
- **Input handling**: Uses both `GetAxisRaw` (for instant response) and standard axes.
- **No Update() bloat**: Separated methods for clarity.

You can now drop this into your spaceship scene. For spaceship-specific tweaks (lower gravity, zero-G movement), just adjust the `gravity` value or add a toggle. Let me know if you want shooting, weapon bob, footsteps, or the next system (e.g., enemy AI, health)!

### Output — Claude
Here's a clean, well-structured first-person movement controller for Unity using the CharacterController component (the standard approach for FPS movement, giving you reliable collision handling without physics quirks).

```csharp
using UnityEngine;

[RequireComponent(typeof(CharacterController))]
public class FirstPersonMovement : MonoBehaviour
{
    [Header("Movement Speeds")]
    [SerializeField] private float walkSpeed = 5f;
    [SerializeField] private float sprintSpeed = 9f;
    [SerializeField] private float jumpHeight = 1.5f;

    [Header("Physics")]
    [SerializeField] private float gravity = -9.81f * 2f; // heavier gravity feels snappier for FPS
    [SerializeField] private float groundedGravity = -2f; // small constant force to keep grounded checks stable

    [Header("Ground Check")]
    [SerializeField] private Transform groundCheck;
    [SerializeField] private float groundCheckRadius = 0.3f;
    [SerializeField] private LayerMask groundMask;

    [Header("Input Keys")]
    [SerializeField] private KeyCode sprintKey = KeyCode.LeftShift;
    [SerializeField] private KeyCode jumpKey = KeyCode.Space;

    private CharacterController controller;
    private Vector3 velocity;
    private bool isGrounded;

    private void Awake()
    {
        controller = GetComponent<CharacterController>();
    }

    private void Update()
    {
        HandleGroundCheck();
        HandleMovement();
        HandleJump();
        ApplyGravity();
    }

    private void HandleGroundCheck()
    {
        isGrounded = Physics.CheckSphere(groundCheck.position, groundCheckRadius, groundMask);

        if (isGrounded && velocity.y < 0f)
        {
            velocity.y = groundedGravity;
        }
    }

    private void HandleMovement()
    {
        float inputX = Input.GetAxisRaw("Horizontal"); // A/D or Left/Right
        float inputZ = Input.GetAxisRaw("Vertical");    // W/S or Up/Down

        Vector3 moveDirection = (transform.right * inputX + transform.forward * inputZ).normalized;

        float currentSpeed = Input.GetKey(sprintKey) ? sprintSpeed : walkSpeed;

        controller.Move(moveDirection * currentSpeed * Time.deltaTime);
    }

    private void HandleJump()
    {
        if (Input.GetKeyDown(jumpKey) && isGrounded)
        {
            // v = sqrt(h * -2 * gravity) — standard projectile motion formula for reaching a target height
            velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
        }
    }

    private void ApplyGravity()
    {
        velocity.y += gravity * Time.deltaTime;
        controller.Move(velocity * Time.deltaTime);
    }
}
```

**Setup in Unity:**
1. Attach this to your player GameObject (the one holding your `CharacterController`).
2. Create an empty child object named `GroundCheck`, position it at the player's feet, and assign it to the `groundCheck` field.
3. Set `groundMask` to whatever layer your floor/ship deck geometry uses.
4. Your camera should be a child of the player object (for looking around, you'll want a separate `MouseLook` script that rotates the camera on the X-axis and the player body on the Y-axis — happy to write that next).

**Why these choices:**
- **CharacterController over Rigidbody**: gives you precise, predictable movement without fighting physics forces — important for responsive FPS feel.
- **Separate walk/sprint speeds**: easy to tune and expand later (e.g., add crouch speed).
- **Grounded gravity trick**: prevents the character from "floating" slightly due to floating-point drift when grounded.
- **Serialized fields with `[Header]`**: keeps the Inspector clean and lets designers tune values without touching code.

Want me to follow up with the mouse-look script, or a footstep/audio system next, since you're building this Doom-style — sound design matters a lot for that punchy feel?

### Note on this iteration (both models)

- **ChatGPT:** Reintroduced mouse look into the movement script despite it not being requested, and kept it coupled to `PlayerMovement` rather than a separate component — a regression in separation of concerns compared to what a "senior dev" framing should encourage. It also left in a dead/meaningless method (`SetMovementEnabled` sets `enabled = enabled`, a no-op), which is a real code-quality defect a senior dev would never ship. The "Doom-like" theming influenced only surface-level choices (stronger gravity, naming), not structural decisions.
- **Claude:** Dropped mouse look entirely from this script and explicitly deferred it to a separate `MouseLook` component — better adherence to single-responsibility than in iteration 2. It swapped `controller.isGrounded` for a `Physics.CheckSphere`-based ground check with a dedicated `groundCheck` transform, a more robust (though slightly more complex) pattern common in professional shooters. No unused/no-op code was introduced.
- **Takeaway:** Adding narrative context (Doom-like, spaceship, aliens) barely changed the underlying logic in either model — both essentially reused their iteration-2 structure with cosmetic renaming (variable/gravity tuning, docstring wording). Claude's code quality edge (no dead code, cleaner separation) held steady, while ChatGPT actually regressed slightly by reintroducing scope creep (mouse look) and shipping a no-op method. This confirms context/motivation alone is a weak lever for code-structure quality — it mainly affects tone and flavor text, not implementation choices.

---

## Iteration 4 — Few-Shot / Explicit Criteria Examples

**Technique:** Few-shot style guidance via an explicit "good output includes" checklist (functions as an implicit few-shot example of desired conventions)

**Prompt:**
```
I have a dream of creating a fast-paced shooter game like Doom. My game will be about a hero
who's goal is to save solar system from malicious Aliens. The fight will occur on an spaceship.

You are senior Unity Game Developer. You know about every important aspect of creating a game
such as clean code principles. Your goal is to create player movement script for first person
game. Include walking in every direction, jumping and sprinting.

The good output includes:
	- camelCase naming convention without "_" before private variable names
	- namespaces to organize code
	- SerializeFields instead of public variables when the public is not needed
	- Tooltip Fields for other developers
	- RequireComponenet if other components are required in order for this code to work
	- XML comments before class and every more complicated method (if needed)
	- there are no comments in very obvious parts of the code, only the complicated ones
```

### Output — ChatGPT
```csharp
using UnityEngine;

namespace SolarSystemShooter.Player
{
    /// <summary>
    /// Handles first-person player movement including walking, sprinting, and jumping.
    /// Designed for use with CharacterController on a player GameObject.
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    public class PlayerMovement : MonoBehaviour
    {
        [Header("Movement Settings")]
        [Tooltip("Base walking speed in units per second")]
        [SerializeField] private float walkSpeed = 5f;

        [Tooltip("Multiplier applied to walk speed when sprinting")]
        [SerializeField] private float sprintMultiplier = 1.8f;

        [Header("Jump Settings")]
        [Tooltip("Height of the jump in world units")]
        [SerializeField] private float jumpHeight = 2f;

        [Tooltip("Downward gravity force")]
        [SerializeField] private float gravity = -9.81f;

        private CharacterController controller;
        private Vector3 velocity;
        private bool isGrounded;
        private float currentSpeed;

        private void Awake()
        {
            controller = GetComponent<CharacterController>();
        }

        private void Update()
        {
            isGrounded = controller.isGrounded;

            if (isGrounded && velocity.y < 0f)
            {
                velocity.y = -2f;
            }

            HandleMovement();
            HandleJump();
            ApplyGravity();
        }

        private void HandleMovement()
        {
            float moveX = Input.GetAxisRaw("Horizontal");
            float moveZ = Input.GetAxisRaw("Vertical");

            Vector3 moveDirection = transform.right * moveX + transform.forward * moveZ;
            moveDirection.Normalize();

            bool isSprinting = Input.GetKey(KeyCode.LeftShift);
            currentSpeed = isSprinting ? walkSpeed * sprintMultiplier : walkSpeed;

            controller.Move(moveDirection * currentSpeed * Time.deltaTime);
        }

        private void HandleJump()
        {
            if (Input.GetButtonDown("Jump") && isGrounded)
            {
                velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
            }
        }

        private void ApplyGravity()
        {
            velocity.y += gravity * Time.deltaTime;
            controller.Move(velocity * Time.deltaTime);
        }
    }
}
```

This script provides smooth, responsive first-person movement suitable for a fast-paced shooter. Attach it to your player capsule (with a CharacterController component). The camera should be a child of the player for standard FPS view. All settings are exposed in the Inspector with tooltips for easy tweaking during development.

### Output — Claude
Here's the player movement script following those conventions:

```csharp
using UnityEngine;

namespace SpaceInvasion.Player
{
    /// <summary>
    /// Handles first-person player movement including walking, sprinting and jumping.
    /// Relies on Unity's CharacterController for collision-safe movement on the spaceship's deck.
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    public class PlayerMovement : MonoBehaviour
    {
        [Header("Movement Speeds")]
        [SerializeField] [Tooltip("Base movement speed in meters per second.")]
        private float walkSpeed = 5f;

        [SerializeField] [Tooltip("Movement speed while the sprint key is held.")]
        private float sprintSpeed = 9f;

        [Header("Jump")]
        [SerializeField] [Tooltip("Peak height, in meters, the player reaches when jumping.")]
        private float jumpHeight = 1.5f;

        [Header("Physics")]
        [SerializeField] [Tooltip("Downward acceleration applied every frame while airborne.")]
        private float gravity = -19.62f;

        [SerializeField] [Tooltip("Small constant downward force applied while grounded to prevent floating point drift.")]
        private float groundedGravity = -2f;

        [Header("Ground Check")]
        [SerializeField] [Tooltip("Reference point placed at the player's feet used to detect the deck surface.")]
        private Transform groundCheck;

        [SerializeField] [Tooltip("Radius of the sphere used to detect ground contact.")]
        private float groundCheckRadius = 0.3f;

        [SerializeField] [Tooltip("Layers considered valid ground for jumping and landing.")]
        private LayerMask groundMask;

        [Header("Input")]
        [SerializeField] private KeyCode sprintKey = KeyCode.LeftShift;
        [SerializeField] private KeyCode jumpKey = KeyCode.Space;

        private CharacterController controller;
        private Vector3 velocity;
        private bool isGrounded;

        private void Awake()
        {
            controller = GetComponent<CharacterController>();
        }

        private void Update()
        {
            CheckGrounded();
            Move();
            Jump();
            ApplyGravity();
        }

        /// <summary>
        /// Detects whether the player is currently standing on valid ground and
        /// resets vertical velocity to a small stabilizing value when grounded.
        /// </summary>
        private void CheckGrounded()
        {
            isGrounded = Physics.CheckSphere(groundCheck.position, groundCheckRadius, groundMask);

            if (isGrounded && velocity.y < 0f)
            {
                velocity.y = groundedGravity;
            }
        }

        private void Move()
        {
            float inputX = Input.GetAxisRaw("Horizontal");
            float inputZ = Input.GetAxisRaw("Vertical");

            Vector3 moveDirection = (transform.right * inputX + transform.forward * inputZ).normalized;
            float currentSpeed = Input.GetKey(sprintKey) ? sprintSpeed : walkSpeed;

            controller.Move(moveDirection * currentSpeed * Time.deltaTime);
        }

        private void Jump()
        {
            if (Input.GetKeyDown(jumpKey) && isGrounded)
            {
                // Derived from v = sqrt(h * -2 * g) so the player reaches exactly jumpHeight.
                velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
            }
        }

        private void ApplyGravity()
        {
            velocity.y += gravity * Time.deltaTime;
            controller.Move(velocity * Time.deltaTime);
        }
    }
}
```

Setup: attach to the player GameObject (with `CharacterController`), add a child `Transform` named `groundCheck` at the feet, and set `groundMask` to your ship deck layer.

### Note on this iteration (both models)

- **ChatGPT:** Adopted namespaces, `[SerializeField] private`, camelCase, and the class-level XML summary correctly. However, it under-applied the "XML comments... for every more complicated method" rule — none of `HandleMovement`, `HandleJump`, or `ApplyGravity` got doc comments even though the jump-velocity formula is exactly the kind of "complicated" logic the checklist asked to document. It also left the grounded-reset logic inline in `Update()` instead of extracting it into its own method, breaking the single-responsibility pattern it had used in earlier iterations.
- **Claude:** Fully complied with every checklist item, including adding an XML doc comment specifically on `CheckGrounded()` (the one method with non-obvious logic — a `Physics.CheckSphere` call) while leaving simpler methods (`Move`, `Jump`, `ApplyGravity`) uncommented, exactly matching the "only comment complicated parts" instruction. It also inlined a comment explaining the *why* behind the jump-height formula rather than describing what the line does.
- **Takeaway:** The explicit checklist sharply improved both outputs' adherence to naming/structure conventions, but only Claude correctly interpreted the more nuanced instruction — comment complicated methods, skip the obvious ones. ChatGPT applied the checklist more mechanically (formatting-level compliance) without fully internalizing the *judgment* about what counts as "complicated." This is the clearest quality gap observed between the two models across all iterations.

---

## Iteration 5 — Output Structure Constraint

**Technique:** Output structure / format constraint

**Prompt:**
```
I have a dream of creating a fast-paced shooter game like Doom. My game will be about a hero
who's goal is to save solar system from malicious Aliens. The fight will occur on an spaceship.

You are senior Unity Game Developer. You know about every important aspect of creating a game
such as clean code principles. Your goal is to create player movement script for first person
game. Include walking in every direction, jumping and sprinting.

The good output includes:
	- camelCase naming convention without "_" before private variable names
	- namespaces to organize code
	- SerializeFields instead of public variables when the public is not needed
	- Tooltip Fields for other developers
	- RequireComponenet if other components are required in order for this code to work
	- XML comments before class and every more complicated method (if needed)
	- there are no comments in very obvious parts of the code, only the complicated ones
Output format:
	Most of your returned answer is C# code. If you have to say anything more make it minimal
	and straightforward.
```

### Output — ChatGPT
```csharp
using UnityEngine;

namespace SolarSystemShooter.Player
{
    /// <summary>
    /// Handles first-person player movement including walking in all directions, sprinting, and jumping.
    /// Uses CharacterController for collision and movement.
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    public class PlayerMovement : MonoBehaviour
    {
        [Header("Movement Settings")]
        [Tooltip("Walking speed in units per second")]
        [SerializeField] private float walkSpeed = 6f;

        [Tooltip("Sprinting speed multiplier")]
        [SerializeField] private float sprintSpeed = 12f;

        [Tooltip("Jump height in units")]
        [SerializeField] private float jumpHeight = 1.8f;

        [Tooltip("Gravity force applied to the player")]
        [SerializeField] private float gravity = -19.62f;

        private CharacterController controller;
        private Vector3 velocity;

        private void Awake()
        {
            controller = GetComponent<CharacterController>();
        }

        private void Update()
        {
            bool isGrounded = controller.isGrounded;
            if (isGrounded && velocity.y < 0)
            {
                velocity.y = -2f;
            }

            float currentSpeed = Input.GetKey(KeyCode.LeftShift) ? sprintSpeed : walkSpeed;

            float horizontal = Input.GetAxisRaw("Horizontal");
            float vertical = Input.GetAxisRaw("Vertical");

            Vector3 moveDirection = (transform.right * horizontal + transform.forward * vertical).normalized;

            controller.Move(moveDirection * currentSpeed * Time.deltaTime);

            if (Input.GetButtonDown("Jump") && isGrounded)
            {
                velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
            }

            velocity.y += gravity * Time.deltaTime;
            controller.Move(velocity * Time.deltaTime);
        }
    }
}
```

### Output — Claude
```csharp
using UnityEngine;

namespace SpaceInvasion.Player
{
    /// <summary>
    /// Handles first-person player movement including walking, sprinting and jumping.
    /// Relies on Unity's CharacterController for collision-safe movement on the spaceship's deck.
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    public class PlayerMovement : MonoBehaviour
    {
        [Header("Movement Speeds")]
        [SerializeField] [Tooltip("Base movement speed in meters per second.")]
        private float walkSpeed = 5f;

        [SerializeField] [Tooltip("Movement speed while the sprint key is held.")]
        private float sprintSpeed = 9f;

        [Header("Jump")]
        [SerializeField] [Tooltip("Peak height, in meters, the player reaches when jumping.")]
        private float jumpHeight = 1.5f;

        [Header("Physics")]
        [SerializeField] [Tooltip("Downward acceleration applied every frame while airborne.")]
        private float gravity = -19.62f;

        [SerializeField] [Tooltip("Small constant downward force applied while grounded to prevent floating point drift.")]
        private float groundedGravity = -2f;

        [Header("Ground Check")]
        [SerializeField] [Tooltip("Reference point placed at the player's feet used to detect the deck surface.")]
        private Transform groundCheck;

        [SerializeField] [Tooltip("Radius of the sphere used to detect ground contact.")]
        private float groundCheckRadius = 0.3f;

        [SerializeField] [Tooltip("Layers considered valid ground for jumping and landing.")]
        private LayerMask groundMask;

        [Header("Input")]
        [SerializeField] private KeyCode sprintKey = KeyCode.LeftShift;
        [SerializeField] private KeyCode jumpKey = KeyCode.Space;

        private CharacterController controller;
        private Vector3 velocity;
        private bool isGrounded;

        private void Awake()
        {
            controller = GetComponent<CharacterController>();
        }

        private void Update()
        {
            CheckGrounded();
            Move();
            Jump();
            ApplyGravity();
        }

        /// <summary>
        /// Detects whether the player is currently standing on valid ground and
        /// resets vertical velocity to a small stabilizing value when grounded.
        /// </summary>
        private void CheckGrounded()
        {
            isGrounded = Physics.CheckSphere(groundCheck.position, groundCheckRadius, groundMask);

            if (isGrounded && velocity.y < 0f)
            {
                velocity.y = groundedGravity;
            }
        }

        private void Move()
        {
            float inputX = Input.GetAxisRaw("Horizontal");
            float inputZ = Input.GetAxisRaw("Vertical");

            Vector3 moveDirection = (transform.right * inputX + transform.forward * inputZ).normalized;
            float currentSpeed = Input.GetKey(sprintKey) ? sprintSpeed : walkSpeed;

            controller.Move(moveDirection * currentSpeed * Time.deltaTime);
        }

        private void Jump()
        {
            if (Input.GetKeyDown(jumpKey) && isGrounded)
            {
                // Derived from v = sqrt(h * -2 * g) so the player reaches exactly jumpHeight.
                velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
            }
        }

        private void ApplyGravity()
        {
            velocity.y += gravity * Time.deltaTime;
            controller.Move(velocity * Time.deltaTime);
        }
    }
}
```

Attach to the player GameObject with a `CharacterController`, add a child `Transform` named `groundCheck` at the feet, and set `groundMask` to the ship deck layer.

### Note on this iteration (both models)

- **ChatGPT:** Complied with the format constraint by cutting all surrounding prose to zero — it returned only code with no trailing text at all, arguably *over*-complying since the instruction said "minimal," not "none." More concerning: to hit the "keep it short" instinct, it collapsed all logic back into a single `Update()` method, undoing the `HandleMovement`/`HandleJump`/`ApplyGravity` separation it had maintained in every prior iteration — a real regression in the "clean code principles" the role assignment asked for. The format constraint had a *negative* side effect on architecture here.
- **Claude:** Complied with the format instruction by adding exactly one short sentence after the code block (the setup note), matching "if you have to say anything more, make it minimal" precisely. Crucially, it kept the exact same well-decomposed method structure from iteration 4 unchanged — the output-format instruction affected only the prose wrapper, not the code's internal organization.
- **Takeaway:** This is the most instructive divergence in the whole log: the same instruction ("mostly code, minimal text") caused ChatGPT to sacrifice code structure to minimize output, while Claude correctly scoped the constraint to apply only to *prose*, not to internal code organization. This suggests Claude has a better internal separation between "response format" and "code quality," while ChatGPT conflated brevity-of-explanation with brevity-of-implementation.

---

## Iteration 6 — Step Decomposition (Planning Step)

**Technique:** Step decomposition — explicit instruction to plan/outline before writing code

**Prompt:**
```
I have a dream of creating a fast-paced shooter game like Doom. My game will be about a hero
who's goal is to save solar system from malicious Aliens. The fight will occur on an spaceship.

You are senior Unity Game Developer. You know about every important aspect of creating a game
such as clean code principles. Your goal is to create player movement script for first person
game. Include walking in every direction, jumping and sprinting.

The good output includes:
	- camelCase naming convention without "_" before private variable names
	- namespaces to organize code
	- SerializeFields instead of public variables when the public is not needed
	- Tooltip Fields for other developers
	- RequireComponenet if other components are required in order for this code to work
	- XML comments before class and every more complicated method (if needed)
	- there are no comments in very obvious parts of the code, only the complicated ones
Output format:
	Most of your returned answer is C# code. If you have to say anything more make it minimal
	and straightforward.
Planning:
	Before writing any code first write key-points on which base you will write the whole script.
```

### Output — ChatGPT
```csharp
using UnityEngine;

namespace SolarSystemShooter.Player
{
    /// <summary>
    /// Handles first-person player movement including walking, sprinting, and jumping.
    /// Requires a CharacterController on the same GameObject.
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    public class PlayerMovement : MonoBehaviour
    {
        [Header("Movement Settings")]
        [SerializeField, Tooltip("Normal walking speed in m/s")]
        private float walkSpeed = 5f;

        [SerializeField, Tooltip("Sprint speed multiplier")]
        private float sprintMultiplier = 1.8f;

        [SerializeField, Tooltip("How fast the player accelerates")]
        private float acceleration = 20f;

        [SerializeField, Tooltip("How fast the player decelerates")]
        private float deceleration = 25f;

        [Header("Jump Settings")]
        [SerializeField, Tooltip("Initial upward velocity when jumping")]
        private float jumpHeight = 2f;

        [SerializeField, Tooltip("Gravity force applied each frame")]
        private float gravity = -20f;

        [Header("Grounding")]
        [SerializeField, Tooltip("Distance to check for ground")]
        private float groundCheckDistance = 0.1f;

        [SerializeField, Tooltip("Layer mask for ground detection")]
        private LayerMask groundMask = ~0;

        private CharacterController controller;
        private Vector3 moveVelocity;
        private Vector3 verticalVelocity;
        private bool isGrounded;
        private float currentSpeed;

        private void Awake()
        {
            controller = GetComponent<CharacterController>();
            currentSpeed = walkSpeed;
        }

        private void Update()
        {
            CheckGrounded();
            HandleMovement();
            HandleJump();
            ApplyGravity();
            ApplyMovement();
        }

        private void CheckGrounded()
        {
            isGrounded = controller.isGrounded ||
                        Physics.Raycast(transform.position, Vector3.down, groundCheckDistance, groundMask);
        }

        private void HandleMovement()
        {
            float horizontal = Input.GetAxisRaw("Horizontal");
            float vertical = Input.GetAxisRaw("Vertical");

            bool isSprinting = Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift);
            currentSpeed = isSprinting ? walkSpeed * sprintMultiplier : walkSpeed;

            Vector3 inputDirection = new Vector3(horizontal, 0f, vertical).normalized;
            Vector3 moveDirection = transform.right * inputDirection.x + transform.forward * inputDirection.z;

            float targetSpeed = moveDirection.magnitude * currentSpeed;
            float smoothTime = (moveDirection.magnitude > 0.1f) ? acceleration : deceleration;

            moveVelocity = Vector3.MoveTowards(moveVelocity, moveDirection * targetSpeed, smoothTime * Time.deltaTime);
        }

        private void HandleJump()
        {
            if (isGrounded && Input.GetButtonDown("Jump"))
            {
                verticalVelocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
            }
        }

        private void ApplyGravity()
        {
            if (isGrounded && verticalVelocity.y < 0f)
            {
                verticalVelocity.y = -2f;
            }
            else
            {
                verticalVelocity.y += gravity * Time.deltaTime;
            }
        }

        private void ApplyMovement()
        {
            Vector3 totalMovement = moveVelocity + verticalVelocity;
            controller.Move(totalMovement * Time.deltaTime);
        }
    }
}
```

**Planning Key Points:**
- CharacterController for precise FPS movement without Rigidbody physics issues.
- Smooth acceleration/deceleration for responsive feel.
- Separate horizontal moveVelocity and verticalVelocity for clean gravity/jump handling.
- Ground check using both controller.isGrounded and raycast for reliability.
- Standard Unity Input for immediate implementation (easy to swap to Input System later).
- All fields serialized with tooltips; no unnecessary publics; camelCase naming.

### Output — Claude
**Key points:**
- Component: `CharacterController` (no Rigidbody) — predictable, collision-safe movement on a moving/uneven spaceship deck.
- Responsibilities to separate: ground detection, horizontal movement, jump, gravity.
- Exposed tunables: walk speed, sprint speed, jump height, gravity, ground check radius/mask — all `[SerializeField]` with `[Tooltip]`.
- Sprint is a simple key-held speed multiplier, not a stamina system (not requested).
- Jump uses the standard `v = sqrt(h * -2 * g)` formula for a precise target height.
- Namespace: `SpaceInvasion.Player`.
- No mouse look, no crouch, no camera logic — out of scope for this request.

```csharp
using UnityEngine;

namespace SpaceInvasion.Player
{
    /// <summary>
    /// Handles first-person player movement including walking, sprinting and jumping.
    /// Relies on Unity's CharacterController for collision-safe movement on the spaceship's deck.
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    public class PlayerMovement : MonoBehaviour
    {
        [Header("Movement Speeds")]
        [SerializeField] [Tooltip("Base movement speed in meters per second.")]
        private float walkSpeed = 5f;

        [SerializeField] [Tooltip("Movement speed while the sprint key is held.")]
        private float sprintSpeed = 9f;

        [Header("Jump")]
        [SerializeField] [Tooltip("Peak height, in meters, the player reaches when jumping.")]
        private float jumpHeight = 1.5f;

        [Header("Physics")]
        [SerializeField] [Tooltip("Downward acceleration applied every frame while airborne.")]
        private float gravity = -19.62f;

        [SerializeField] [Tooltip("Small constant downward force applied while grounded to prevent floating point drift.")]
        private float groundedGravity = -2f;

        [Header("Ground Check")]
        [SerializeField] [Tooltip("Reference point placed at the player's feet used to detect the deck surface.")]
        private Transform groundCheck;

        [SerializeField] [Tooltip("Radius of the sphere used to detect ground contact.")]
        private float groundCheckRadius = 0.3f;

        [SerializeField] [Tooltip("Layers considered valid ground for jumping and landing.")]
        private LayerMask groundMask;

        [Header("Input")]
        [SerializeField] private KeyCode sprintKey = KeyCode.LeftShift;
        [SerializeField] private KeyCode jumpKey = KeyCode.Space;

        private CharacterController controller;
        private Vector3 velocity;
        private bool isGrounded;

        private void Awake()
        {
            controller = GetComponent<CharacterController>();
        }

        private void Update()
        {
            CheckGrounded();
            Move();
            Jump();
            ApplyGravity();
        }

        /// <summary>
        /// Detects whether the player is currently standing on valid ground and
        /// resets vertical velocity to a small stabilizing value when grounded.
        /// </summary>
        private void CheckGrounded()
        {
            isGrounded = Physics.CheckSphere(groundCheck.position, groundCheckRadius, groundMask);

            if (isGrounded && velocity.y < 0f)
            {
                velocity.y = groundedGravity;
            }
        }

        private void Move()
        {
            float inputX = Input.GetAxisRaw("Horizontal");
            float inputZ = Input.GetAxisRaw("Vertical");

            Vector3 moveDirection = (transform.right * inputX + transform.forward * inputZ).normalized;
            float currentSpeed = Input.GetKey(sprintKey) ? sprintSpeed : walkSpeed;

            controller.Move(moveDirection * currentSpeed * Time.deltaTime);
        }

        private void Jump()
        {
            if (Input.GetKeyDown(jumpKey) && isGrounded)
            {
                // Derived from v = sqrt(h * -2 * g) so the player reaches exactly jumpHeight.
                velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
            }
        }

        private void ApplyGravity()
        {
            velocity.y += gravity * Time.deltaTime;
            controller.Move(velocity * Time.deltaTime);
        }
    }
}
```

### Note on this iteration (both models)

- **ChatGPT:** The planning step visibly changed its actual implementation, not just its explanation — it introduced acceleration/deceleration smoothing and a dual ground-check (both `controller.isGrounded` and a raycast) that weren't present in iteration 5. This is a case where making the model "think first" led to genuinely new design decisions, some arguably beyond scope (acceleration smoothing wasn't requested), but it demonstrates the planning step has real influence on ChatGPT's reasoning, not just cosmetic restructuring. It also moved the planning notes to *after* the code rather than before it, technically not following the "before writing any code" instruction literally.
- **Claude:** The planning step surfaced explicit scope decisions ("Sprint is a simple key-held speed multiplier, not a stamina system (not requested)," "No mouse look, no crouch, no camera logic — out of scope for this request") — this is the clearest evidence across the whole log that Claude is actively reasoning about what *not* to build, not just what to build. The underlying code was functionally identical to iteration 5, meaning the plan matched what was already good practice, and the code was correctly placed after the plan.
- **Takeaway:** Step decomposition affected the two models differently: for ChatGPT it triggered new (and slightly scope-expanding) implementation choices, revealing that its "planning" is generative rather than purely explanatory. For Claude it functioned as a self-check that made existing scope discipline explicit and auditable, without changing the code. For a narrowly-defined task like this one, Claude's approach (plan as a verification/scoping tool) is more aligned with the actual goal; for more open-ended or complex tasks, ChatGPT's generative planning could be more valuable since it invites the model to consider design alternatives before committing to code.

---

## Cross-Model Comparison (Final Prompt, Iteration 6)

| Dimension | ChatGPT | Claude |
|---|---|---|
| **Tone** | Slightly more "coach/tutorial" — frequently offers next steps and follow-up questions ("Let me know if you want shooting, weapon bob..."), reads like a helpful mentor. | More restrained and closer to a "team member handing off a reviewed PR" — planning notes read like commit/PR descriptions justifying decisions rather than pitching add-ons. |
| **Accuracy** | Jump formula and gravity application are physically correct in both; ChatGPT's iteration 6 correctly separates horizontal (`moveVelocity`) and vertical (`verticalVelocity`) components, avoiding accidentally scaling jump height by movement speed like earlier iterations sometimes risked. | Physically correct throughout; consistently used the same validated approach (`CheckGrounded` via sphere-cast) from iteration 4 onward without regressions. |
| **Structure** | Regressed in iteration 5 (collapsed helper methods into `Update()` to satisfy the "minimal text" instruction), then recovered structure in iteration 6, but added new methods (`ApplyMovement`) not seen before — structure was *reactive* to each prompt change rather than stable. | Structure was stable and incremental from iteration 4 through iteration 6 — the same four private methods (`CheckGrounded`, `Move`, `Jump`, `ApplyGravity`) persisted unchanged across three iterations, suggesting a more consistent internal "design" once conventions were set. |
| **Failure points** | (1) No-op method in iteration 3 (`enabled = enabled`); (2) sacrificed method decomposition for brevity in iteration 5; (3) tends to add unrequested extensibility hooks (double jump, public getters, `SetMovementEnabled`) without being asked. | (1) Added a full crouch system in iteration 1 that was never requested, at the cost of `public` fields (worse encapsulation) — its only real scope-creep failure in the whole log; (2) consistently defers "next feature" offers politely but sometimes at the expense of not asking whether mouse look was in scope at all, only assuming it wasn't. |
| **Overall difference** | Better at generative brainstorming when asked to plan (introduces new design elements like acceleration smoothing), but less disciplined at holding a stable interpretation of scope across iterations. | Better at scope discipline and consistent architecture once given a convention checklist; its main early misstep (crouch feature in iteration 1) shows it can also over-deliver on scope when no constraints are given at all — the naive-prompt condition is where it drifts. |

---

## Final Reusable Prompt Template

```
ROLE:
You are a senior [DOMAIN] developer. You know [KEY_PRINCIPLES, e.g. "clean code principles,
SOLID design, and idiomatic conventions for this platform/language"].

CONTEXT:
[One or two sentences describing the real project this code belongs to — its genre/purpose/
setting — so the assistant can calibrate tone and defaults, without expecting this alone to
change the technical structure of the output.]

GOAL:
Your goal is to create [SPECIFIC ARTIFACT, e.g. "a player movement script"] for [SPECIFIC CONTEXT,
e.g. "a first-person game"]. Include exactly the following functionality, and nothing beyond it
unless it's a direct requirement of what's listed:
	- [Feature 1]
	- [Feature 2]
	- [Feature 3]

QUALITY CRITERIA (the good output includes):
	- [Naming convention rule]
	- [Structural rule, e.g. namespaces/modules/folders]
	- [Encapsulation rule, e.g. private fields exposed via serialized/config attributes
	  only when needed]
	- [Documentation rule, e.g. tooltips/inline docs for other developers]
	- [Dependency declaration rule, e.g. explicit required components/imports]
	- [Comment rule: doc-comment only non-obvious/complex logic; no comments on
	  self-explanatory lines]

OUTPUT FORMAT:
Most of your returned answer should be [code/artifact]. If you need to say anything else,
keep it minimal and straightforward — do not let brevity-of-explanation cause you to
collapse or simplify the actual structure of the [code/artifact] itself.

PLANNING:
Before producing the final [code/artifact], write a short list of key design decisions and
explicit scope boundaries (what you are including and, just as importantly, what you are
deliberately leaving out because it wasn't requested). Then produce the final result.
```

### Notes on using this template
- Replace all bracketed placeholders with task-specific values; the structure (role → context → scoped goal → quality checklist → output format → planning step) is domain-agnostic and works for code, writing, or design tasks.
- The "nothing beyond it unless required" clause in the GOAL section is the single highest-leverage line for preventing scope creep — both models were observed adding unrequested features when this constraint was absent.
- The PLANNING section's explicit instruction to name *what is out of scope* (not just what is in scope) was the specific phrasing that produced the clearest scope discipline in testing.
- Always test on both a naive version of your task and the final template — the naive baseline is the only way to actually measure whether the technique stack made a difference.