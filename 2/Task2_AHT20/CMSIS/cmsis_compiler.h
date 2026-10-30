#ifndef __CMSIS_COMPILER_H
#define __CMSIS_COMPILER_H

#include <stdint.h>

/* ?? ARM Compiler 6 (ARMCLANG) */
#if defined (__ARMCC_VERSION) && (__ARMCC_VERSION >= 6010050)
  #define __ASM            __asm
  #define __INLINE         __inline
  #define __STATIC_INLINE  static __inline

  #define __NO_RETURN      __attribute__((noreturn))
  #define __USED           __attribute__((used))
  #define __WEAK           __attribute__((weak))
  #define __PACKED         __attribute__((packed))
  #define __PACKED_STRUCT  struct __attribute__((packed))
  #define __UNALIGNED_UINT32(x)  (*((__packed uint32_t *)(x)))

  #define __BKPT(value)    __asm volatile ("bkpt "#value)
  #define __NOP()          __asm volatile ("nop")
  #define __WFI()          __asm volatile ("wfi")
  #define __WFE()          __asm volatile ("wfe")
  #define __SEV()          __asm volatile ("sev")
  #define __ISB()          __asm volatile ("isb 0xF":::"memory")
  #define __DSB()          __asm volatile ("dsb 0xF":::"memory")
  #define __DMB()          __asm volatile ("dmb 0xF":::"memory")

  #define __CORTEX_M       (0x03U)
#endif

#endif
