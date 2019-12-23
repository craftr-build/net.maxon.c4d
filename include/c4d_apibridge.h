/**
 * Copyright (c) 2018  Niklas Rosenstein
 *
 * This work is free. You can redistribute it and/or modify it under the
 * terms of the Do What The Fuck You Want To Public License, Version 2,
 * as published by Sam Hocevar. See the COPYING file for more details.
 *
 * Note: This header is not associated with or endorsed by MAXON or the
 * MAXON SDK Support Team. Using this header may complicate future SDK
 * support requests.
 */

#pragma once
#include "c4d.h"
#include "c4d_falloffdata.h"
#include "vector4.h"
#include "lib_description.h"

#define C4D_APIBRIDGE_CONCAT(x, y) PRIVATE_C4D_APIBRIDGE_CONCAT(x, y)
#define PRIVATE_C4D_APIBRIDGE_CONCAT(x, y) x##y

// C4D_APIBRIDGE_COMMANDDATA_EXECUTE, C4D_APIBRIDGE_COMMANDDATA_GETPARENTMANAGER
#if API_VERSION < 20000
  #define C4D_APIBRIDGE_COMMANDDATA_EXECUTE(doc) \
    virtual Bool Execute(BaseDocument* doc) override

  #define C4D_APIBRIDGE_COMMANDDATA_EXECUTE_IMPL(cls, doc) \
    Bool cls::Execute(BaseDocument* doc)

  #define C4D_APIBRIDGE_COMMANDDATA_GETSTATE(doc) \
    virtual Int32 GetState(BaseDocument* doc) override

  #define C4D_APIBRIDGE_COMMANDDATA_GETSTATE_IMPL(cls, doc) \
    Int32 cls::GetState(BaseDocument* doc)

  #define C4D_APIBRIDGE_COMMANDDATA_GETPARENTMANAGER() static_cast<GeDialog*>(nullptr)
#else
  #define C4D_APIBRIDGE_COMMANDDATA_EXECUTE(doc) \
    virtual Bool Execute(BaseDocument* doc, GeDialog* __parentManager) override

  #define C4D_APIBRIDGE_COMMANDDATA_EXECUTE_IMPL(cls, doc) \
    Bool cls::Execute(BaseDocument* doc, GeDialog* __parentManager)

  #define C4D_APIBRIDGE_COMMANDDATA_GETSTATE(doc) \
    virtual Int32 GetState(BaseDocument* doc, GeDialog* __parentManager) override

  #define C4D_APIBRIDGE_COMMANDDATA_GETSTATE_IMPL(cls, doc) \
    Int32 cls::GetState(BaseDocument* doc, GeDialog* __parentManager)

  #define C4D_APIBRIDGE_COMMANDDATA_GETPARENTMANAGER() __parentManager
#endif

// operator "" _s
#if API_VERSION < 20000
  inline String operator "" _s(char const* s, size_t l) {
    String result(l, 0);
    for (UInt i = 0; i < l; ++i) result[i] = s[i];
    return result;
  }
#endif

// GePrint
#if API_VERSION >= 20000
  inline void GePrint(char const* s) {
    GePrint(maxon::String(s));
  }
#endif

// MessageDialog
#if API_VERSION >= 20000
  inline void MessageDialog(char const* s) {
    MessageDialog(maxon::String(s));
  }
#endif

// StatusSetText
#if API_VERSION >= 20000
  inline void StatusSetText(char const* s) {
    StatusSetText(String(s));
  }
#endif

// Deg, Rad
#if API_VERSION >= 20000
  inline Float32 Deg(Float32 r) { return maxon::RadToDeg(r); }
  inline Float64 Deg(Float64 r) { return maxon::RadToDeg(r); }
  inline Float32 Rad(Float32 r) { return maxon::DegToRad(r); }
  inline Float64 Rad(Float64 r) { return maxon::DegToRad(r); }
#endif

// ENUM_END_FLAGS
#if API_VERSION >= 20000
  #define ENUM_END_FLAGS(x) MAXON_ENUM_FLAGS(x)
#endif

// AutoNew, AutoPtr, AutoGeFree
// From the R19 SDK with adjustments.
#if API_VERSION >= 20000

  //----------------------------------------------------------------------------------------
  /// This class handles automatic allocation and deallocation of objects with NewObjClear() and DeleteObj(). Otherwise it is similar in function to AutoAlloc.
  /// @see AutoPtr
  //----------------------------------------------------------------------------------------
  template <class TYPE> class AutoNew
  {
    TYPE* ptr;

  private:
    const AutoNew<TYPE>& operator = (const AutoNew<TYPE>& p);
    AutoNew(const AutoNew<TYPE>& p);

  public:
    //----------------------------------------------------------------------------------------
    /// Calls @link NewObjClear NewObjClear(TYPE)@endlink and stores the returned pointer internally.
    //----------------------------------------------------------------------------------------
    AutoNew() { ptr = NewObjClear(TYPE); }

    //----------------------------------------------------------------------------------------
    /// Calls @link DeleteObj DeleteObj(ptr)@endlink, where @c ptr is the internally stored pointer.
    //----------------------------------------------------------------------------------------
    ~AutoNew() { DeleteObj(ptr); }

    //----------------------------------------------------------------------------------------
    /// Conversion to a raw pointer to @c TYPE. Makes it possible to pass the object directly to functions like @c Function(TYPE* t).
    /// @return												The internal pointer. The AutoNew instance owns the pointed object.
    //----------------------------------------------------------------------------------------
    operator TYPE*()
    {
      return ptr;
    }

    //----------------------------------------------------------------------------------------
    /// Conversion to a reference to @c TYPE. Makes it possible to pass the object directly to functions like @c Function(TYPE& t).
    /// @note This dereferences the internal pointer. Hence, it must not be @formatConstant{nullptr}.
    /// @return												A reference to the pointed object.
    //----------------------------------------------------------------------------------------
    operator TYPE&()
    {
      return *ptr;
    }

    //----------------------------------------------------------------------------------------
    /// Used for calls like @c myauto->Function().
    /// @note This dereferences the internal pointer. Hence, it must not be @formatConstant{nullptr}.
    /// @return												The internal pointer. The AutoNew instance owns the pointed object.
    //----------------------------------------------------------------------------------------
    TYPE* operator -> () const { return ptr; }

    //----------------------------------------------------------------------------------------
    /// Used for expressions like &myauto. Extracts a pointer to the internal pointer.
    /// @note This means that it is impossible to get the address of the actual AutoNew instance.
    /// @return												A pointer to the internal pointer. The AutoNew instance owns the pointed object.
    //----------------------------------------------------------------------------------------
    TYPE* const* operator & () const { return &ptr; }

    //----------------------------------------------------------------------------------------
    /// Retrieves the internal pointer and then sets it to @formatConstant{nullptr}. Thus the ownership is transfered to the caller.
    /// @return												The internal pointer. The caller takes over the ownership of the pointed object.
    //----------------------------------------------------------------------------------------
    TYPE* Release() { TYPE* tmp = ptr; ptr = nullptr; return tmp; }

    //----------------------------------------------------------------------------------------
    /// Calls @link DeleteObj DeleteObj(ptr)@endlink with the internal pointer and sets it to @formatConstant{nullptr}.
    //----------------------------------------------------------------------------------------
    void Free() { DeleteObj(ptr); }

    //----------------------------------------------------------------------------------------
    /// Assigns @formatParam{p} as the internal pointer.
    /// @param[in] p									A pointer to an object allocated with NewObjClear(). The AutoNew instance takes over the ownership of the pointed object.
    //----------------------------------------------------------------------------------------
    void Assign(TYPE* p) { ptr = p; }
  };

  //----------------------------------------------------------------------------------------
  /// This class handles automatic deallocation of objects with ::DeleteObj(). It is similar in function to AutoNew, but the object has to have been previously allocated.
  /// @see AutoNew
  //----------------------------------------------------------------------------------------
  template <class TYPE> class AutoPtr
  {
    TYPE* ptr;

  private:
    const AutoPtr<TYPE>& operator = (const AutoPtr<TYPE>& p);
    AutoPtr(const AutoPtr<TYPE>& p);

  public:
    //----------------------------------------------------------------------------------------
    /// Stores the pointer @formatParam{p} internally.
    /// @param[in] p									A pointer to an object allocated with NewObjClear. The AutoPtr instance takes over the ownership of the pointed object.
    //----------------------------------------------------------------------------------------
    explicit AutoPtr(TYPE* p) { ptr = p; }

    //----------------------------------------------------------------------------------------
    /// Calls @link DeleteObj DeleteObj(ptr)@endlink, where @c ptr is the internally stored pointer.
    //----------------------------------------------------------------------------------------
    ~AutoPtr() { DeleteObj(ptr); }

    //----------------------------------------------------------------------------------------
    /// Conversion to a raw pointer to @c TYPE. Makes it possible to pass the object directly to functions like @c Function(TYPE* t).
    /// @return												The internal pointer. The AutoPtr instance owns the pointed object.
    //----------------------------------------------------------------------------------------
    operator TYPE*() const { return ptr; }

    //----------------------------------------------------------------------------------------
    /// Conversion to a reference to @c TYPE. Makes it possible to pass the object directly to functions like @c Function(TYPE& t).
    /// @note This dereferences the internal pointer. Hence, it must not be @formatConstant{nullptr}.
    /// @return												A reference to the pointed object.
    //----------------------------------------------------------------------------------------
    operator TYPE&() const { return *ptr; }

    //----------------------------------------------------------------------------------------
    /// Used for calls like @c myauto->Function().
    /// @note This dereferences the internal pointer. Hence, it must not be @formatConstant{nullptr}.
    /// @return												The internal pointer. The AutoPtr instance owns the pointed object.
    //----------------------------------------------------------------------------------------
    TYPE* operator -> () const { return ptr; }

    //----------------------------------------------------------------------------------------
    /// Used for expressions like @c &myauto. Extracts a pointer to the internal pointer.
    /// @note This means that it is impossible to get the address of the actual AutoPtr instance.
    /// @return												A pointer to the internal pointer. The AutoPtr instance owns the pointed object.
    //----------------------------------------------------------------------------------------
    TYPE* const* operator & () const { return &ptr; }

    //----------------------------------------------------------------------------------------
    /// Retrieves the internal pointer and then sets it to @formatConstant{nullptr}. Thus the ownership is transfered to the caller.
    /// @return												The internal pointer. The caller takes over the ownership of the pointed object.
    //----------------------------------------------------------------------------------------
    TYPE* Release() { TYPE* tmp = ptr; ptr = nullptr; return tmp; }

    //----------------------------------------------------------------------------------------
    /// Calls @link DeleteObj DeleteObj(ptr)@endlink with the internal pointer and sets it to @formatConstant{nullptr}.
    //----------------------------------------------------------------------------------------
    void Free() { DeleteObj(ptr); }

    //----------------------------------------------------------------------------------------
    /// Assigns @formatParam{p} as the internal pointer.
    /// @param[in] p									A pointer to an object allocated with NewObjClear(). The AutoPtr instance takes over the ownership of the pointed object.
    //----------------------------------------------------------------------------------------
    void Assign(TYPE* p) { ptr = p; }

    //----------------------------------------------------------------------------------------
    /// Retrieves the internal pointer.
    /// @return												The internal pointer.
    //----------------------------------------------------------------------------------------
    TYPE* Get() { return ptr; }
  };

  //----------------------------------------------------------------------------------------
  /// This class handles automatic deallocation of memory with DeleteMem().
  /// @see NewMemClear
  //----------------------------------------------------------------------------------------
  template <class TYPE> class AutoGeFree
  {
    TYPE* ptr;

  private:
    TYPE* operator = (TYPE* p);

  public:
    //----------------------------------------------------------------------------------------
    /// Default constructor.
    //----------------------------------------------------------------------------------------
    AutoGeFree() { ptr = nullptr; }

    // NOTE: Added for R20 compatibility with NewMemClear()
    AutoGeFree(maxon::ResultPtr<TYPE>&& value) : AutoGeFree(value.UncheckedGetValue()) {}

    //----------------------------------------------------------------------------------------
    /// Stores the pointer @formatParam{p} internally.
    /// @param[in] p									A pointer to the block of memory to be freed with DeleteMem(). The AutoGeFree instance takes over the ownership of the pointed object.
    //----------------------------------------------------------------------------------------
    explicit AutoGeFree(TYPE* p) { ptr = p; }

    //----------------------------------------------------------------------------------------
    /// Calls @link DeleteMem DeleteMem(ptr)@endlink, where @c ptr is the internally stored pointer.
    //----------------------------------------------------------------------------------------
    ~AutoGeFree() { DeleteMem(ptr); ptr = nullptr; }

    //----------------------------------------------------------------------------------------
    /// Sets @formatParam{p} as the internal pointer.
    /// @param[in] p									A pointer to the block of memory to be freed with DeleteMem(). The AutoGeFree instance takes over the ownership of the pointed object.
    //----------------------------------------------------------------------------------------
    void Set(TYPE* p) { ptr = p; }

    //----------------------------------------------------------------------------------------
    /// Conversion to a raw pointer to @c TYPE. Makes it possible to pass the object directly to functions like @c Function(TYPE* t).
    /// @return												The internal pointer. The AutoGeFree instance owns the pointed object.
    //----------------------------------------------------------------------------------------
    operator TYPE*() const { return ptr; }

    //----------------------------------------------------------------------------------------
    /// Used for calls like @c myauto->Function().
    /// @note This dereferences the internal pointer. Hence, it must not be @formatConstant{nullptr}.
    /// @return												The internal pointer. The AutoGeFree instance owns the pointed object.
    //----------------------------------------------------------------------------------------
    TYPE* operator -> () const { return ptr; }

    //----------------------------------------------------------------------------------------
    /// Used for expressions like @c &myauto. Extracts a pointer to the internal pointer.
    /// @note This means that it is impossible to get the address of the actual AutoGeFree instance.
    /// @return												A pointer to the internal pointer. The AutoGeFree instance owns the pointed object.
    //----------------------------------------------------------------------------------------
    TYPE* const* operator & () const { return &ptr; }

    //----------------------------------------------------------------------------------------
    /// Retrieves the internal pointer and then sets it to @formatConstant{nullptr}. Thus the ownership is transfered to the caller.
    /// @return												The internal pointer. The caller takes over the ownership of the pointed object.
    //----------------------------------------------------------------------------------------
    TYPE* Release() { TYPE* tmp = ptr; ptr = nullptr; return tmp; }

    //----------------------------------------------------------------------------------------
    /// Calls @link DeleteMem DeleteMem(ptr)@endlink with the internal pointer and sets it to @formatConstant{nullptr}.
    //----------------------------------------------------------------------------------------
    void Free() { DeleteMem(ptr); ptr = nullptr; }

    //----------------------------------------------------------------------------------------
    /// Assigns @formatParam{p} as the internal pointer.
    /// @param[in] p									A pointer to an object to be freed with DeleteMem(). The AutoGeFree instance takes over the ownership of the pointed object.
    //----------------------------------------------------------------------------------------
    void Assign(TYPE* p) { ptr = p; }
  };

#endif

// GetVector3
#if API_VERSION >= 20000
  inline Vector GetVector3(Vector4d const& v) {
    return v.GetVector3();
  }
#endif

// GetMacAddress
#if API_VERSION >= 20000
  #include "maxon/network_ip.h"
  inline Bool GetMacAddress(maxon::BaseArray<UChar>& macAddress) {
    iferr (maxon::BaseArray<UChar> addr = maxon::NetworkIpInterface::GetMacAddress()) {
      return false;
    }
    macAddress = std::move(addr);
    return true;
  }
#endif

// BMP_EMBOSSED
#if API_VERSION >= 21000
  #define BMP_EMBOSSED BMP_GRAYEDOUT
#endif

namespace c4d_apibridge {

  #if API_VERSION >= 20000
    using String = maxon::String;
  #else
    using String = ::String;
  #endif

  // ==== Result Unpacking
  // =====================

  #if API_VERSION >= 20000
    template <typename T>
    inline T* Unpack(maxon::ResultPtr<T>&& ptr) {
      return std::move(ptr.UncheckedGetValue());
    }

    template <typename T>
    inline T Unpack(maxon::Result<T>&& result) {
      return std::move(result.GetValue());
    }

    template <typename T>
    inline T* Unpack(maxon::ResultRef<T>&& ref) {
      return ref.GetPointer();
    }
  #else
    template <typename T>
    inline T* Unpack(T*&& ptr) {
      return std::forward<T*>(ptr);
    }
  #endif

  // ==== API Member Compatibility Helpers
  // =====================================

  namespace M {

    #if API_VERSION >= 20000
      #define PRIVATE_C4D_APIBRIDGE_MAToff(x) (x.off)
      #define PRIVATE_C4D_APIBRIDGE_MATv1(x) (x.sqmat.v1)
      #define PRIVATE_C4D_APIBRIDGE_MATv2(x) (x.sqmat.v2)
      #define PRIVATE_C4D_APIBRIDGE_MATv3(x) (x.sqmat.v3)
    #else
      #define PRIVATE_C4D_APIBRIDGE_MAToff(x) (x.off)
      #define PRIVATE_C4D_APIBRIDGE_MATv1(x) (x.v1)
      #define PRIVATE_C4D_APIBRIDGE_MATv2(x) (x.v2)
      #define PRIVATE_C4D_APIBRIDGE_MATv3(x) (x.v3)
    #endif

    #define PRIVATE_C4D_APIBRIDGE_MATACCESSOR(Member) \
      inline Vector& M##Member(Matrix& m) { return PRIVATE_C4D_APIBRIDGE_MAT##Member(m); } \
      inline Vector const& M##Member(Matrix const& m) { return PRIVATE_C4D_APIBRIDGE_MAT##Member(m); }

    PRIVATE_C4D_APIBRIDGE_MATACCESSOR(off)
    PRIVATE_C4D_APIBRIDGE_MATACCESSOR(v1)
    PRIVATE_C4D_APIBRIDGE_MATACCESSOR(v2)
    PRIVATE_C4D_APIBRIDGE_MATACCESSOR(v3)

  }

  using namespace M;

  inline Bool IsEmpty(String const& s) {
    #if API_VERSION >= 20000
    return s.IsEmpty();
    #else
    return !s.Content();
    #endif
  }
  inline Bool IsEmpty(Filename const& f) {
    #if API_VERSION >= 20000
    return !f.IsPopulated();
    #else
    return !f.Content();
    #endif
  }
  inline Bool IsEmpty(C4DUuid const& u) {
    #if API_VERSION >= 20000
    if (u.IsPopulated()) {
      return u == C4DUuid(EC);
    }
    return true;
    #else
    return !u.Content();
    #endif
  }

  #if API_VERSION >= 20000
    inline DescID const& GetDescriptionID(DescriptionBaseMessage const* desc) {
      return desc->_descId;
    }
    inline DescID& GetDescriptionID(DescriptionBaseMessage* desc) {
      return desc->_descId;
    }
    inline Int32 GetDescriptionChosen(DescriptionPopup const* desc) {
      return desc->_chosen;
    }
    inline BaseContainer const* GetDescriptionMsg(DescriptionPopup const* desc) {
      return desc->_msg;
    }
    inline BaseContainer& GetDescriptionPopup(DescriptionPopup* desc) {
      return desc->_popup;
    }
  #else
    #define _DEF(Type, Member) \
      inline DescID const& GetDescriptionID(Type const* desc) { \
        return desc->Member; \
      } \
      inline DescID& GetDescriptionID(Type* desc) { \
        return desc->Member; \
      }
    _DEF(DescriptionCheckDragAndDrop, id)
    _DEF(DescriptionCommand, id)
    #if API_VERSION >= 19000
    _DEF(DescriptionCustomGuiNotification, _descId)
    #endif
    _DEF(DescriptionGetObjects, descid)
    _DEF(DescriptionPopup, id)
    #undef _DEF
    inline Int32 GetDescriptionChosen(DescriptionPopup const* desc) {
      return desc->chosen;
    }
    inline BaseContainer const* GetDescriptionMsg(DescriptionPopup const* desc) {
      return desc->msg;
    }
    inline BaseContainer& GetDescriptionPopup(DescriptionPopup* desc) {
      return desc->popup;
    }
  #endif

  inline maxon::BaseArray<Filename> GetGlobalTexturePaths() {
    maxon::BaseArray<Filename> result;
    #if API_VERSION >= 20000
      // TODO: GetValue() is not safe, I guess.?
      TexturePathList lst = Unpack(::GetGlobalTexturePaths());
      for (auto&& item : lst) {
        (void) result.Append(Unpack(item.Get<0>().GetSystemPath()));
      }
    #else
      result.EnsureCapacity(8);
      for (Int i = 0; i < 10; ++i) {
        Filename temp = GetGlobalTexturePath(i);
        if (temp.Content()) result.Append(std::move(temp));
      }
    #endif
    return result;
  }

  inline void NormalizeW(Vector4d& v) {
    #if API_VERSION >= 20000
      v.NormalizeW();
    #else
      v.MakeVector3();
    #endif
  }

  inline void Normalize(Matrix& m) {
    #if API_VERSION >= 20000
        m = m.GetNormalized();
    #else
        m.Normalize();
    #endif
  }

  inline Int32 GetDirty(C4D_Falloff* falloff, BaseDocument* doc, BaseContainer* bc = nullptr) {
    #if API_VERSION >= 20000
      return falloff->GetDirty(doc, bc);
    #else
      return falloff->GetDirty(bc);
    #endif
  }

  inline Matrix4d Invert(Matrix4d const& m) {
    #if API_VERSION >= 20000
      return ~m;
    #else
      return !m;
    #endif
  }

  inline Matrix Invert(Matrix const& m) {
    #if API_VERSION >= 15000
      return ~m;
    #else
      return !m;
    #endif
  }

  inline void SetGradientInterpolation(Gradient* grad, Int32 mode) {
    #if API_VERSION >= 20000
      for (Int32 i = 0; i < grad->GetKnotCount(); ++i) {
        auto knot = grad->GetKnot(i);
        knot.interpolation = mode;
        grad->SetKnot(i, knot);
      }
    #else
      grad->SetData(GRADIENT_INTERPOLATION, GRADIENT_INTERPOLATION_NONE);
    #endif
  }

  inline void SetBranchInfoName(BranchInfo& obj, String const* name) {
    #if API_VERSION >= 20000
      if (name) obj.name = *name;
      else obj.name = ""_s;
    #else
      obj.name = name; // Note: Caller owns the pointed string
    #endif
  }

  inline GeResource& GlobalResource() {
    #if API_VERSION >= 20000
      return ::g_resource;
    #else
      return ::resource;
    #endif
  }

  // ====== Backwards compatible datastructures
  // ==========================================

  #if API_VERSION >= 20000
    #define PRIVATE_C4D_APIBRIDGE_HASHMAP_SUPER maxon::HashMap<K, V, HASH, GET_KEY, ALLOCATOR, false>
    #define PRIVATE_C4D_APIBRIDGE_HASHMAP_DEFAULTHASH maxon::DefaultCompare
  #else
    #define PRIVATE_C4D_APIBRIDGE_HASHMAP_SUPER maxon::HashMap<K, V, HASH, GET_KEY, ALLOCATOR>
    #define PRIVATE_C4D_APIBRIDGE_HASHMAP_DEFAULTHASH maxon::DefaultHash
  #endif

  template <
    typename K,
    typename V,
    typename HASH=PRIVATE_C4D_APIBRIDGE_HASHMAP_DEFAULTHASH,
    typename GET_KEY=maxon::HashMapKeyValuePair,
    typename ALLOCATOR=maxon::DefaultAllocator>
  class HashMap : public PRIVATE_C4D_APIBRIDGE_HASHMAP_SUPER {
    using Super = PRIVATE_C4D_APIBRIDGE_HASHMAP_SUPER;
  public:
    using Super::Super;

    #if API_VERSION >= 20000
    inline typename Super::Entry* FindEntry(K const& key) { return this->Find(key); }
    inline typename Super::Entry const* FindEntry(K const& key) const { return this->Find(key); }
    inline typename Super::Entry* FindOrCreateEntry(K const& key, maxon::Bool& created) { return this->InsertEntry(key, created).GetPointer(); }
    inline typename Super::Entry* Put(K const& key, V const& value) { return this->Insert(key, value).GetPointer(); }
    inline Bool Remove(K const& k) { return this->Erase(k).GetValue(); }
    inline void Remove(typename Super::Entry* e) { this->Erase(this->GetIterator(e)); }
    // TODO: More backwards compatibility functions
    #endif
  };

  #if API_VERSION >= 21000
    #define PRIVATE_C4D_APIBRIDGE_HASHSET_SUPER maxon::HashSet<T, HASH, maxon::HashMapKeyValuePair, ALLOCATOR, false>
  #elif API_VERSION >= 20000
    #define PRIVATE_C4D_APIBRIDGE_HASHSET_SUPER maxon::HashSet<T, HASH, ALLOCATOR, false>
  #else
    #define PRIVATE_C4D_APIBRIDGE_HASHSET_SUPER maxon::HashSet<T, HASH, ALLOCATOR>
  #endif

  template <
    typename T,
    typename HASH=PRIVATE_C4D_APIBRIDGE_HASHMAP_DEFAULTHASH,
    typename ALLOCATOR=maxon::DefaultAllocator>
  class HashSet : public PRIVATE_C4D_APIBRIDGE_HASHSET_SUPER {
    using Super = PRIVATE_C4D_APIBRIDGE_HASHSET_SUPER;
  public:
    using Super::Super;

    #if API_VERSION >= 20000
    inline T const* Add(T const& value) { return this->InsertKey(value).GetPointer(); }
    inline T const* Add(T const& value, maxon::Bool& added) { return this->InsertKey(value, added).GetPointer(); }
    #endif
  };

}

// iferr(), ifnoerr() for R19
#if API_VERSION < 20000

  // Note: If you include any other C4D API headers after this one and that
  // C4D API header uses their own iferr()/ifnoerr(), you may need to include
  // the header before the c4d_apibridge.
  #ifdef iferr
    #undef iferr
  #endif
  #ifdef ifnoerr
    #undef ifnoerr
  #endif

  #define PRIVATE_iferr_handler_(ErrType, ErrName, ...) \
    c4d_apibridge::detail::ErrType ErrName; \
    __VA_ARGS__ % ErrName; \
    if (ErrName.Catch())
  #define iferr(...) PRIVATE_iferr_handler_(Error, C4D_APIBRIDGE_CONCAT(tmperr_, __COUNTER__), __VA_ARGS__)
  #define ifnoerr(...) PRIVATE_iferr_handler_(NoError, C4D_APIBRIDGE_CONCAT(tmperr_, __COUNTER__), __VA_ARGS__)

  namespace c4d_apibridge {
  namespace detail {

    template <typename T>
    struct PtrUnpack {
      T* _ptr;
      PtrUnpack(T* ptr) : _ptr(ptr) { }
      inline operator T& () { DebugAssert(_ptr); return *_ptr; }
      inline operator T* () { return _ptr; }
    };

    template <typename T>
    struct PtrUnpack<AutoAlloc<T>> {
      AutoAlloc<T>* _ptr;
      PtrUnpack(AutoAlloc<T>* ptr) : _ptr(ptr) { }
      inline operator T& () { DebugAssert(_ptr); DebugAssert(*_ptr); return * (T*)(*this); }
      inline operator T* () { if (_ptr) return (T*) (*_ptr); return nullptr; }
    };

    class Error {
    protected:
      Bool _ok = false;
    public:
      inline Bool Catch() const { return !_ok; }

      template <typename T>
      friend inline PtrUnpack<T> operator % (T*&& value, Error& self) {
        if (value) {
          self._ok = true;
          return std::forward<T*>(value);
        }
        else {
          self._ok = false;
          return (T*)nullptr;
        }
      }

      friend inline Bool operator %(Bool const& value, Error& self) {
        self._ok = value;
        return value;
      }

    };
    class NoError : public Error {
    public:
      inline Bool Catch() const { return _ok; }
    };
  }
  }

#else

  /**
  * @func operator % ()
  *
  * Error-handling operators for the @ref iferr and @ref iferrno macros
  * when using expressions that return a pointers instead of a #maxon::Result.
  * This is possible in R19 with our implementation of @ref iferr and
  * @ref iferrno, thus it is important we make it possible in R20 as well.
  */
  template <typename T>
  inline T* operator %(T*&& value, maxon::ThreadReferencedError& err) {
    if (MAXON_LIKELY(value != nullptr)) {
      err = nullptr;
    }
    else {
      // Use CreateErrorPtr() because the compiler can omit the call if the err isn't used.
      err = CreateErrorPtr(MAXON_SOURCE_LOCATION, maxon::ERROR_TYPE::OUT_OF_MEMORY);
    }
    return std::forward<T*>(value);
  }

  inline nullptr_t operator %(nullptr_t, maxon::ThreadReferencedError& err) {
    // Use CreateErrorPtr() because the compiler can omit the call if the err isn't used.
    err = CreateErrorPtr(MAXON_SOURCE_LOCATION, maxon::ERROR_TYPE::OUT_OF_MEMORY);
    return nullptr;
  }

#endif

#if API_VERSION >= 20000
  #ifdef CUSTOMTYPE_HIDE_ID
    #undef CUSTOMTYPE_HIDE_ID
  #endif
#endif

#include "c4d_apibridge_enums.h"
